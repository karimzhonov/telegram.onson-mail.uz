from django.core.exceptions import ValidationError
from import_export import resources

from users.models import Client, ClientId

from .models import Order


class OrderResource(resources.ModelResource):
    part = resources.Field("part__number")
    client = resources.Field("client__fio")
    passport = resources.Field("client__passport", readonly=True)

    class Meta:
        model = Order
        exclude = ["products", "id", "with_online_buy"]
        import_id_fields = ["number"]

    def before_import_row(self, row, row_number=None, **kwargs):
        row.update(part=kwargs.get("form_data").get("part"))
        row.update(date=kwargs.get("form_data").get("date"))
        if not row.get("number"):
            raise ValidationError(message=f"{row} - number invalid")
        if not Client.objects.filter(pnfl=row.get("client")).exists():
            if ClientId.objects.filter(id_str=row.get("clientid")).exists():
                raise ValidationError(f"{row.get('client')} - not found")
            return row.update(client=None)
        client = Client.objects.filter(pnfl=row.get("client")).first()
        row.update(client=client)
        try:
            weight = str(row.get("weight"))
            weight = float(weight.replace(",", "."))
            row.update(weight=weight)
        except ValueError:
            raise ValidationError(message=f"{row.get('weight')} - invalid weight")
        
        try:
            facture_price = str(row.get("facture_price"))
            facture_price = float(facture_price.replace(",", "."))
            row.update(facture_price=facture_price)
        except ValueError:
            raise ValidationError(message=f"{row.get('facture_price')} - invalid facture_price")


    def get_or_init_instance(self, instance_loader, row):
        if not row.get("client"):
            row.import_type = resources.RowResult.IMPORT_TYPE_SKIP
            return None, False
        instance = Order.objects.create(
            part=row.get("part"),
            number=row.get("number"),
            clientid=row.get("clientid"),
            client=row.get("client"),
            name=row.get("name"),
            weight=row.get("weight"),
            facture_price=row.get("facture_price"),
            date=row.get("date")
        )
        row.update(part=row.get("part").id)
        row.update(client=row.get("client").id)
        row.import_type = resources.RowResult.IMPORT_TYPE_SKIP
        return instance, True
        
    def import_obj(self, obj, data, dry_run, **kwargs):
        if not obj:
            return
        return super().import_obj(obj, data, dry_run, **kwargs)
    
    def save_instance(self, instance, is_create, using_transactions=True, dry_run=False):
        if not instance:
            return
        return super().save_instance(instance, is_create, using_transactions, dry_run)
    