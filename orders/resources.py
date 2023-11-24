from import_export import resources
from import_export.widgets import ForeignKeyWidget
from django.core.exceptions import ValidationError
from users.models import Client
from .models import Order


class OrderResource(resources.ModelResource):

    class Meta:
        model = Order
        import_id_fields = ["number"]

    def get_import_fields(self):
        return super().get_import_fields()

    def before_import_row(self, row, row_number=None, **kwargs):
        row.update(part=kwargs.get("form_data").get("part"))
        row.update(date=kwargs.get("form_data").get("date"))
        if not row.get("number"):
            raise ValidationError()
        if not Client.objects.filter(pnfl=row.get("client")).exists():
            raise ValidationError()
        client = Client.objects.filter(pnfl=row.get("client")).first()
        row.update(client=client)

    def get_or_init_instance(self, instance_loader, row):
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
