from django.db import connection


class MaterializedViewMixin:
    sql = None

    @classmethod
    def refresh_view(cls):
        with connection.cursor() as cursor:
            cursor.execute(f"REFRESH MATERIALIZED VIEW {cls._meta.db_table}")

    @classmethod
    def create_view(cls):
        with connection.cursor() as cursor:
            sql = """
            drop materialized view if exists {db_table};
            create materialized view {view} as {sql};""".format(
                view=connection.ops.quote_name(cls._meta.db_table), 
                sql=cls.sql, db_table=cls._meta.db_table
            )
            cursor.execute(sql)
