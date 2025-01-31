import tablib
from import_export.formats.base_formats import XLSX


class OrderXLSX(XLSX):
    def create_dataset(self, in_stream):
        from io import BytesIO

        import openpyxl

        # 'data_only' means values are read from formula cells, not the formula itself
        xlsx_book = openpyxl.load_workbook(
            BytesIO(in_stream), read_only=True, data_only=True
        )

        dataset = tablib.Dataset()
        sheet = xlsx_book.active

        # obtain generator
        rows = sheet.rows
        [next(rows) for _ in range(9)]
        dataset.headers = [cell.value for cell in next(rows)]
        for row in rows:
            if row[9].value and row[1].value:
                row_values = [cell.value for cell in row]
                dataset.append(row_values)
        return dataset