import os
from django.conf import settings
from django.db.models import F, Value
from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from bot.filters.db_filter import DbSearchFilter
from bot.filters.prefix import Prefix
from bot.models import get_text as _
from bot.states import OnlineBuy
from bot.text_keywords import ONLINE_BUY_MENU, REMOVE_PRODUCT_TO_CHOSEN, NEXT, PREVIEW, ADD_PRODUCT_TO_CART, ONLINE_BUY_CHOSEN, PLUS, MINUS
from storages.models import Product, ProductImage, ProductToChosen, ProductToCart
from users.models import ClientId
from orders.models import Cart


def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(ONLINE_BUY_CHOSEN))(my_chosens)
    dp.callback_query(Prefix("chosen"))(product_action)
    dp.message(DbSearchFilter("online_buy_chosen_clear"))(clear_chosen)


async def my_chosens(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if not await ProductToChosen.objects.filter(clientid__user_id=msg.from_user.id, clientid__storage_id=data["storage"]).aexists():
        return await msg.answer(_("online_buy_chosen_empty_text", msg.bot.lang))
    async for pch in ProductToChosen.objects.select_related("product__category").prefetch_related("product__category__translations").filter(clientid__user_id=msg.from_user.id, clientid__storage_id=data["storage"]):
        image = await ProductImage.objects.filter(product_id=pch.product_id).order_by("id").afirst()
        await _render_product(pch.product, image, msg, state, False, msg.from_user.id)
    await state.set_state(OnlineBuy.chosen)
    await msg.answer(_("online_buy_chosen_text", msg.bot.lang), reply_markup=ReplyKeyboardBuilder([
        [types.KeyboardButton(text=_("online_buy_chosen_clear", msg.bot.lang))],
        [types.KeyboardButton(text=_(ONLINE_BUY_MENU, msg.bot.lang))]
    ]).as_markup(resize_keyboard=True))


async def _render_product(product: Product, image: ProductImage,  msg: types.Message, state: FSMContext, edit=False, user_id=None, delete=False):
    data = await state.get_data()
    text = product.product_to_text(msg.bot.lang)
    keyboard = InlineKeyboardBuilder()
    if image:
        paginator = []
        if await ProductImage.objects.filter(product_id=product.id).exclude(id__gte=image.id).aexists():
            paginator.append(types.InlineKeyboardButton(text=PREVIEW, callback_data=f"chosen:paginate_product:{product.id}:{image.id}:{PREVIEW}"))
        else:
            paginator.append(types.InlineKeyboardButton(text=PREVIEW, callback_data="null"))
        offset = await ProductImage.objects.filter(product=product).exclude(id__gt=image.id).order_by("id").acount()
        count = await ProductImage.objects.filter(product=product).acount()
        paginator.append(types.InlineKeyboardButton(text=f"{_('images', msg.bot.lang)} {offset}/{count}", callback_data="count"))
        if await ProductImage.objects.filter(product_id=product.id).exclude(id__lte=image.id).aexists():
            paginator.append(types.InlineKeyboardButton(text=NEXT, callback_data=f"chosen:paginate_product:{product.id}:{image.id}:{NEXT}"))
        else:
            paginator.append(types.InlineKeyboardButton(text=NEXT, callback_data="null"))
        keyboard.row(*paginator)
    keyboard.row(types.InlineKeyboardButton(text=_(REMOVE_PRODUCT_TO_CHOSEN, msg.bot.lang), callback_data=f"chosen:{REMOVE_PRODUCT_TO_CHOSEN}:{product.id}:{getattr(image, 'id', 0)}"))
    
    if not await ProductToCart.objects.filter(product=product, cart__clientid__user_id=user_id, cart__clientid__storage_id=data["storage"]).aexists():
        keyboard.row(types.InlineKeyboardButton(text=_(ADD_PRODUCT_TO_CART, msg.bot.lang), callback_data=f"chosen:{ADD_PRODUCT_TO_CART}:{product.id}:{getattr(image, 'id', 0)}"))
    else:
        count = await ProductToCart.objects.filter(product=product, cart__clientid__user_id=user_id, cart__clientid__storage_id=data["storage"]).afirst()
        keyboard.row(
            types.InlineKeyboardButton(text=_(MINUS, msg.bot.lang), callback_data=f"chosen:{MINUS}:{product.id}:{getattr(image, 'id', 0)}"),
            types.InlineKeyboardButton(text=str(count.count), callback_data=f"count"),
            types.InlineKeyboardButton(text=_(PLUS, msg.bot.lang), callback_data=f"chosen:{PLUS}:{product.id}:{getattr(image, 'id', 0)}"),
        )
    if edit:
        if image:
            await msg.edit_media(
                types.InputMediaPhoto(media=types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "media", str(image.image))), caption=text),
                reply_markup=keyboard.as_markup(resize_keyboard=True)
            )
        else:
            await msg.edit_reply_markup(reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        await msg.answer_photo(
            types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "media", str(image.image))), text, reply_markup=keyboard.as_markup(resize_keyboard=True)
        ) if image else await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


async def product_action(cq: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = cq.message
    type, *cq_data_list = cq.data.split(":")
    if cq_data_list[0] == "paginate_product":
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        current_image_id = cq_data_list[2]
        images = ProductImage.objects.filter(product_id=product.id)
        image = await images.exclude(id__lte=current_image_id).order_by("id").afirst() if cq_data_list[-1] == NEXT else await images.exclude(id__gte=current_image_id).order_by("id").alast()
        if not image:
            return
        return await _render_product(product, image, msg, state, True, cq.from_user.id)
    elif cq_data_list[0] == REMOVE_PRODUCT_TO_CHOSEN:
        await ProductToChosen.objects.filter(
            product_id=cq_data_list[1], clientid=await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        ).adelete()
        return await msg.delete()
    elif cq_data_list[0] == ADD_PRODUCT_TO_CART:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        my_cart, created = await Cart.objects.aget_or_create(clientid=clientid)
        await ProductToCart.objects.acreate(
            product_id=cq_data_list[1], cart=my_cart
        )
        image = await ProductImage.objects.filter(id=cq_data_list[2]).afirst()
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        return await _render_product(product, image, msg, state, True, cq.from_user.id)
    elif cq_data_list[0] == PLUS:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        my_cart, created = await Cart.objects.aget_or_create(clientid=clientid)
        await ProductToCart.objects.filter(
            product_id=cq_data_list[1], cart=my_cart).aupdate(count=F("count") + Value(1)
        )
        image = await ProductImage.objects.filter(id=cq_data_list[2]).afirst()
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        return await _render_product(product, image, msg, state, True, cq.from_user.id)
    elif cq_data_list[0] == MINUS:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        my_cart, created = await Cart.objects.aget_or_create(clientid=clientid)
        pc = await ProductToCart.objects.filter(
            product_id=cq_data_list[1], cart=my_cart
        ).afirst()
        await ProductToCart.objects.filter(
            product_id=cq_data_list[1], cart=my_cart).aupdate(count=F("count") - Value(1)
        ) if pc and pc.count > 1 else await ProductToCart.objects.filter(
            product_id=cq_data_list[1], cart=my_cart
        ).adelete()
        image = await ProductImage.objects.filter(id=cq_data_list[2]).afirst()
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        return await _render_product(product, image, msg, state, True, cq.from_user.id)


async def clear_chosen(msg: types.Message, state: FSMContext):
    from . import storage_menu_back

    data = await state.get_data()
    await ProductToChosen.objects.filter(clientid__user_id=msg.from_user.id, clientid__storage_id=data["storage"]).adelete()
    await storage_menu_back(msg, state)
