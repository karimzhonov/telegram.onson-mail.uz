from import_export import resources
from .models import ClientId, Client


class ClientIdResource(resources.ModelResource):
    fio = resources.Field("selected_client__fio", "ФИО")
    passport = resources.Field("selected_client__passport", "Пасспорт")
    pnfl = resources.Field("selected_client__pnfl", "ПИНФЛ")
    phone = resources.Field("selected_client__phone", "Номер телефона")
    address = resources.Field("selected_client__address", "Адрес")
    id_str = resources.Field("get_id", "ID")

    class Meta:
        model = ClientId
        fields = ["id_str", "fio", "passport", "pnfl", "phone", "address"]

    def before_import_row(self, row, row_number=None, **kwargs):
        row.update(storage=kwargs.get("form_data").get("storage").id)

    def get_or_init_instance(self, instance_loader, row):
        if row.get("passport") and row.get("pnfl"):
            client, created = Client.objects.get_or_create({
                "pnfl": row.get("pnfl"),
                "passport": row.get("passport"),
                "fio": row.get("fio"),
                "phone": row.get("phone"),
                "address": row.get("address")
            }, pnfl=row.get("pnfl"), passport=row.get("passport"))
            if created:
                client_id = ClientId.objects.create(
                    storage_id=row.get("storage"),
                    id_str=row.get("id_str"),
                    selected_client=client
                )
                client_id.clients.add(client)
                return client_id, True
            try:
                client_id = ClientId.objects.get(
                        id_str=row.get("id_str"),
                    )
                return client_id, False
            except ClientId.DoesNotExist:
                client_id = ClientId.objects.create(
                    storage_id=row.get("storage"),
                    id_str=row.get("id_str"),
                    selected_client=client
                )
                client_id.clients.add(client)
                return client_id, True
        row.import_type = resources.RowResult.IMPORT_TYPE_SKIP
        return None, False

    def import_obj(self, obj, data, dry_run, **kwargs):
        if not obj:
            return
        return super().import_obj(obj, data, dry_run, **kwargs)
    
    def save_instance(self, instance, is_create, using_transactions=True, dry_run=False):
        if not instance:
            return
        return super().save_instance(instance, is_create, using_transactions, dry_run)
    