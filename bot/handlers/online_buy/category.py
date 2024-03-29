from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db.models import F, Value

from bot.filters.db_filter import DbSearchFilter
from bot.filters.prefix import Prefix
from bot.models import get_text as _
from bot.states import OnlineBuy
from bot.text_keywords import (ADD_PRODUCT_TO_CART, ADD_PRODUCT_TO_CHOSEN, MINUS, NEXT, ONLINE_BUY_CART,
                               ONLINE_BUY_CATEGORY, ONLINE_BUY_MENU, PLUS, PREVIEW, REMOVE_PRODUCT_TO_CHOSEN, GO_TO_CATEGORY, GO_TO_PRODUCT)
from bot.utils import get_file
from orders.models import Cart
from storages.models import Category, Product, ProductImage, ProductToCart, ProductToChosen
from users.models import ClientId

LIMIT = 5

def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(ONLINE_BUY_CATEGORY))(my_category)
    dp.message(OnlineBuy.category)(entered_category)
    dp.message(OnlineBuy.product)(entered_category)
    dp.callback_query(Prefix("category"))(product_action)
    dp.callback_query(Prefix(GO_TO_CATEGORY))(go_to_category)
    dp.callback_query(Prefix(GO_TO_PRODUCT))(go_to_product)

async def _alert_clientid(cq: types.CallbackQuery, clientid: ClientId):
    if not clientid:
        await cq.answer(_("need_clientid_to_use_this_operation", cq.message.bot.lang), True)
        return True
    return False


async def my_category(msg: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardBuilder()
    data = await state.get_data()
    if not data.get("category"):
        categories = Category.objects.prefetch_related("translations").translated(msg.bot.lang).filter(is_active=True, parent__isnull=True)
    else:
        categories = Category.objects.prefetch_related("translations").translated(msg.bot.lang).filter(is_active=True, parent_id=data.get("category"))
        if not await categories.aexists():
            cat = await Category.objects.aget(id=data.get("category"))
            categories = Category.objects.prefetch_related("translations").translated(msg.bot.lang).filter(is_active=True, parent_id=cat.parent_id)
    if not await categories.aexists():
        return await msg.answer(_("category_list_empty", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    async for category in categories:
        await sync_to_async(category.set_current_language)(msg.bot.lang)
        all_cats = [c.id async for c in Category.objects.filter_recursive(id=category.id)]
        keyboard.row(types.KeyboardButton(text=f"{category.name} ({await Product.objects.filter(category_id__in=all_cats, storage_id=data.get('storage')).acount()})"))
    keyboard.row(types.KeyboardButton(text=_(ONLINE_BUY_MENU, msg.bot.lang)))
    await msg.answer(_("online_buy_category_list_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(OnlineBuy.category)


async def entered_category(msg: types.Message, state: FSMContext):
    try:
        text = " ".join(msg.text.split(" ")[:-1])
        category = await Category.objects.prefetch_related("translations").aget(translations__name=text)
        await state.update_data(
            category=category.id,
            offset=0
        )
        if await Category.objects.prefetch_related("translations").translated(msg.bot.lang).filter(is_active=True, parent_id=category.id).aexists():
            return await my_category(msg, state)
        await my_products(msg, state)
    except Category.DoesNotExist:
        await msg.answer(_("invalid_category", msg.bot.lang))


async def my_products(msg: types.Message, state: FSMContext, offset=0, user_id=None):
    user_id = msg.from_user.id if not user_id else user_id
    data = await state.get_data()
    products = Product.objects.select_related("category").prefetch_related("category__translations").filter(category_id=data["category"], category__translations__language_code=msg.bot.lang, storage_id=data.get('storage')).order_by("-created_date")
    if not await products.aexists():
        return await msg.answer(_("online_buy_product_list_empty", msg.bot.lang))
    if offset == 0:
        await msg.answer(_("online_buy_product_list", msg.bot.lang), reply_markup=ReplyKeyboardBuilder([
            [types.KeyboardButton(text=_(ONLINE_BUY_CATEGORY, msg.bot.lang)), types.KeyboardButton(text=_(ONLINE_BUY_CART, msg.bot.lang))]
        ]).as_markup(resize_keyboard=True))
    async for product in products[offset:offset + LIMIT]:
        image = await ProductImage.objects.filter(product=product).order_by("id").afirst()
        await _render_product(product, image, msg, state, False, user_id)
    await state.set_state(OnlineBuy.product)
    products_count = await products.acount()
    text = f"""{_("showed_offset_products_in_count", msg.bot.lang, offset=LIMIT + offset, count=await products.acount())}"""
    keyboard = InlineKeyboardBuilder()
    if LIMIT + offset < products_count:
        keyboard.row(types.InlineKeyboardButton(text=_("show_again", msg.bot.lang), callback_data=f"category:show_again:{offset + LIMIT}"))
        await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


async def _render_product(product: Product, image: ProductImage,  msg: types.Message, state: FSMContext, edit=False, user_id=None, delete=False):
    data = await state.get_data()
    text = product.product_to_text(msg.bot.lang)
    keyboard = InlineKeyboardBuilder()
    if image:
        paginator = []
        if await ProductImage.objects.filter(product_id=product.id).exclude(id__gte=image.id).aexists():
            paginator.append(types.InlineKeyboardButton(text=PREVIEW, callback_data=f"category:paginate_product:{product.id}:{image.id}:{PREVIEW}"))
        else:
            paginator.append(types.InlineKeyboardButton(text=PREVIEW, callback_data="null"))
        offset = await ProductImage.objects.filter(product=product).exclude(id__gt=image.id).order_by("id").acount()
        count = await ProductImage.objects.filter(product=product).acount()
        paginator.append(types.InlineKeyboardButton(text=f"{_('images', msg.bot.lang)} {offset}/{count}", callback_data="count"))
        if await ProductImage.objects.filter(product_id=product.id).exclude(id__lte=image.id).aexists():
            paginator.append(types.InlineKeyboardButton(text=NEXT, callback_data=f"category:paginate_product:{product.id}:{image.id}:{NEXT}"))
        else:
            paginator.append(types.InlineKeyboardButton(text=NEXT, callback_data="null"))
        keyboard.row(*paginator)
    if not await ProductToChosen.objects.filter(product=product, clientid__user_id=user_id, clientid__storage_id=data["storage"]).aexists():
        keyboard.row(types.InlineKeyboardButton(text=_(ADD_PRODUCT_TO_CHOSEN, msg.bot.lang), callback_data=f"category:{ADD_PRODUCT_TO_CHOSEN}:{product.id}:{getattr(image, 'id', 0)}"))
    else:
        keyboard.row(types.InlineKeyboardButton(text=_(REMOVE_PRODUCT_TO_CHOSEN, msg.bot.lang), callback_data=f"category:{REMOVE_PRODUCT_TO_CHOSEN}:{product.id}:{getattr(image, 'id', 0)}"))
    
    if not await ProductToCart.objects.filter(product=product, cart__clientid__user_id=user_id, cart__clientid__storage_id=data["storage"]).aexists():
        keyboard.row(types.InlineKeyboardButton(text=_(ADD_PRODUCT_TO_CART, msg.bot.lang), callback_data=f"category:{ADD_PRODUCT_TO_CART}:{product.id}:{getattr(image, 'id', 0)}"))
    else:
        count = await ProductToCart.objects.filter(product=product, cart__clientid__user_id=user_id, cart__clientid__storage_id=data["storage"]).afirst()
        keyboard.row(
            types.InlineKeyboardButton(text=_(MINUS, msg.bot.lang), callback_data=f"category:{MINUS}:{product.id}:{getattr(image, 'id', 0)}"),
            types.InlineKeyboardButton(text=str(count.count), callback_data=f"count"),
            types.InlineKeyboardButton(text=_(PLUS, msg.bot.lang), callback_data=f"category:{PLUS}:{product.id}:{getattr(image, 'id', 0)}"),
        )
    if edit:
        if image:
            await msg.edit_media(
                types.InputMediaPhoto(media=get_file(str(image.image)), caption=text),
                reply_markup=keyboard.as_markup(resize_keyboard=True)
            )
        else:
            await msg.edit_reply_markup(reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        await msg.answer_photo(
            get_file(str(image.image)), text, reply_markup=keyboard.as_markup(resize_keyboard=True)
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
    elif cq_data_list[0] == "show_again":
        await msg.delete()
        await my_products(msg, state, int(cq_data_list[1]))
    elif cq_data_list[0] == ADD_PRODUCT_TO_CHOSEN:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        alerted = await _alert_clientid(cq, clientid)
        if alerted:
            return
        await ProductToChosen.objects.acreate(
            product_id=cq_data_list[1], clientid=clientid
        )
        image = await ProductImage.objects.filter(id=cq_data_list[2]).afirst()
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        return await _render_product(product, image, msg, state, True, cq.from_user.id)
    elif cq_data_list[0] == REMOVE_PRODUCT_TO_CHOSEN:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        alerted = await _alert_clientid(cq, clientid)
        if alerted:
            return
        await ProductToChosen.objects.filter(
            product_id=cq_data_list[1], clientid=clientid
        ).adelete()
        image = await ProductImage.objects.filter(id=cq_data_list[2]).afirst()
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        return await _render_product(product, image, msg, state, True, cq.from_user.id)
    elif cq_data_list[0] == ADD_PRODUCT_TO_CART:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        alerted = await _alert_clientid(cq, clientid)
        if alerted:
            return
        my_cart, created = await Cart.objects.aget_or_create(clientid=clientid)
        await ProductToCart.objects.acreate(
            product_id=cq_data_list[1], cart=my_cart
        )
        image = await ProductImage.objects.filter(id=cq_data_list[2]).afirst()
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        return await _render_product(product, image, msg, state, True, cq.from_user.id)
    elif cq_data_list[0] == PLUS:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        alerted = await _alert_clientid(cq, clientid)
        if alerted:
            return
        my_cart, created = await Cart.objects.aget_or_create(clientid=clientid)
        await ProductToCart.objects.filter(
            product_id=cq_data_list[1], cart=my_cart).aupdate(count=F("count") + Value(1)
        )
        image = await ProductImage.objects.filter(id=cq_data_list[2]).afirst()
        product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[1])
        return await _render_product(product, image, msg, state, True, cq.from_user.id)
    elif cq_data_list[0] == MINUS:
        clientid = await ClientId.objects.filter(user_id=cq.from_user.id, storage=data["storage"]).afirst()
        alerted = await _alert_clientid(cq, clientid)
        if alerted:
            return
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


async def go_to_category(cq: types.CallbackQuery, state: FSMContext):
    type, *cq_data_list = cq.data.split(":")
    await state.update_data(
        storage=cq_data_list[0],
        category=cq_data_list[1],
        offset=0
    )
    await my_products(cq.message, state, user_id=cq.from_user.id)


async def go_to_product(cq: types.CallbackQuery, state: FSMContext):
    type, *cq_data_list = cq.data.split(":")
    await state.update_data(
        storage=cq_data_list[0],
        category=cq_data_list[1],
        offset=0
    )
    message = await cq.message.answer(_("online_buy_product_list", cq.message.bot.lang), reply_markup=ReplyKeyboardBuilder([
        [types.KeyboardButton(text=_(ONLINE_BUY_CATEGORY, cq.message.bot.lang)), types.KeyboardButton(text=_(ONLINE_BUY_CART, cq.message.bot.lang))]
    ]).as_markup(resize_keyboard=True))
    await message.delete()
    product = await Product.objects.select_related("category").prefetch_related("category__translations").aget(id=cq_data_list[2])
    image = await ProductImage.objects.filter(product=product).order_by("id").afirst()
    await _render_product(product, image, cq.message, state, False, cq.from_user.id)
    await state.set_state(OnlineBuy.product)
