class ReadOnlyAdminModelMixin:
    def has_change_permission(self, request, obj=None, *args, **kwargs) -> bool:
        return False

    def has_add_permission(self, request, *args, **kwargs) -> bool:
        return False

    def has_delete_permission(self, request, obj=None, *args, **kwargs) -> bool:
        return False


def table(array: list[dict], translations: dict, footer=None):
    header = [f'<th class="column-{key}">{value}</th>' for key, value in translations.items()]
    rows = []
    for row in array:
        new_row = []
        for key, value in translations.items():
            new_row.append(f'<td class="field-{key}"><p>{row.get(key)}</p></td>')
        rows.append(f'<tr class="form-row has_original dynamic-order_set" id="order_set-0">{"".join(new_row)}</tr>')
    html = f"""
    <table class="table table-hover text-nowrap" style="width: 100%; margin-top: 30px">
        <thead>
            {"".join(header)}
        </thead>

        <tbody>
            {"".join(rows)}
        </tbody>
   </table>
    """
    if footer:
        html = f"{html}\n{footer}"
    return html
