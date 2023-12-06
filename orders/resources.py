from import_export import resources
from django.core.exceptions import ValidationError

from users.models import Client
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
            raise ValidationError()
        if not Client.objects.filter(pnfl=row.get("client")).exists():
            row.update(client=None)
        client = Client.objects.filter(pnfl=row.get("client")).first()
        row.update(client=client)
        try:
            weight = row.get("weight")    
            weight = float(weight.replace(",", "."))
            row.update(weight=weight)
        except ValueError:
            raise ValidationError(message=f"{row.get('weight')} - invalid weight")


    def get_or_init_instance(self, instance_loader, row):
        if not row.get("client"):
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
        return instance, True
        
    def before_save_instance(self, instance, using_transactions, dry_run):
        print(instance)
