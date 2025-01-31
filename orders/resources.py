from django.core.exceptions import ValidationError
from import_export import resources

from users.models import Client, ClientId

from .models import Order


class OrderResource(resources.ModelResource):
    # part = resources.Field("part__number")
    # passport = resources.Field("client__passport", readonly=True)
    number = resources.Field(column_name='1. Тижорат хужжатининг раками', attribute='number')
    clientid = resources.Field(column_name='2. Халкаро курьерлик жунатмасининг жунатувчиси', attribute='clientid')
    name = resources.Field(column_name='3. Халкаро курьерлик жунатмасининг кабул килувчиси ва унинг манзили', attribute='name')
    client = resources.Field(column_name='4. Халкаро курьерликнинг жунатмасидаги товарларнинг кискача номи', attribute='client')
    weight = resources.Field(column_name='5. Халкаро курьерлик жунатмасининг брутто вазни (кг)', attribute='weight')
    facture_price = resources.Field(column_name='6. Халкаро курьерлик жунатмасининг фактура киймати', attribute='facture_price')

    class Meta:
        model = Order
        exclude = ["products", "id", "with_online_buy"]
        import_id_fields = ["number"]

    def import_field(self, field, instance, row, is_m2m=False, **kwargs):
        if field.attribute == 'part':
            instance.part = kwargs.get('form_data').get('part')
            return
        if field.attribute == 'date':
            instance.date = kwargs.get('form_data').get('date')
            return
        if field.attribute == 'client':
            try:
                client = Client.objects.get(pnfl=row[field.column_name])
            except Client.DoesNotExist:
                client = Client.objects.create(
                    pnfl=row[field.column_name],
                    passport=row[field.column_name],
                    fio=row[field.column_name],
                )
            instance.client = client
            return
        if field.attribute == 'weight':
            try:
                weight = str(row.get(field.column_name))
                weight = float(weight.replace(",", "."))
                instance.weight = weight
                return
            except ValueError:
                raise ValidationError(message=f"{row.get('weight')} - invalid weight")
        if field.attribute == 'facture_price':
            try:
                facture_price = str(row.get(field.column_name))
                facture_price = float(facture_price.replace(",", "."))
                instance.facture_price = facture_price
            except ValueError:
                raise ValidationError(message=f"{row.get('facture_price')} - invalid price")
        return super().import_field(field, instance, row, is_m2m, **kwargs)

    # def before_import_row(self, row, row_number=None, **kwargs):
    #     row.update(part=kwargs.get("form_data").get("part"))
    #     row.update(date=kwargs.get("form_data").get("date"))
    #     if not row.get("number"):
    #         raise ValidationError(message=f"{row} - number invalid")
    #     if not Client.objects.filter(pnfl=row.get("client")).exists():
    #         if ClientId.objects.filter(id_str=row.get("clientid")).exists():
    #             raise ValidationError(f"{row.get('client')} - not found")
    #         return row.update(client=None)
    #     client = Client.objects.filter(pnfl=row.get("client")).first()
    #     row.update(client=client)
    #     try:
    #         weight = str(row.get("weight"))
    #         weight = float(weight.replace(",", "."))
    #         row.update(weight=weight)
    #     except ValueError:
    #         raise ValidationError(message=f"{row.get('weight')} - invalid weight")
    #
    #     try:
    #         facture_price = str(row.get("facture_price"))
    #         facture_price = float(facture_price.replace(",", "."))
    #         row.update(facture_price=facture_price)
    #     except ValueError:
    #         raise ValidationError(message=f"{row.get('facture_price')} - invalid facture_price")


    # def get_or_init_instance(self, instance_loader, row):
    #     if not row.get("client"):
    #         row.import_type = resources.RowResult.IMPORT_TYPE_SKIP
    #         return None, False
    #     instance = Order.objects.create(
    #         part=row.get("part"),
    #         number=row.get("number"),
    #         clientid=row.get("clientid"),
    #         client=row.get("client"),
    #         name=row.get("name"),
    #         weight=row.get("weight"),
    #         facture_price=row.get("facture_price"),
    #         date=row.get("date")
    #     )
    #     row.update(part=row.get("part").id)
    #     row.update(client=row.get("client").id)
    #     row.import_type = resources.RowResult.IMPORT_TYPE_SKIP
    #     return instance, True
    #
    # def import_obj(self, obj, data, dry_run, **kwargs):
    #     if not obj:
    #         return
    #     return super().import_obj(obj, data, dry_run, **kwargs)
    #
    # def save_instance(self, instance, is_create, using_transactions=True, dry_run=False):
    #     if not instance:
    #         return
    #     return super().save_instance(instance, is_create, using_transactions, dry_run)
    #