from typing import Dict, List, Optional

from pg_check_service.pg_connect import PgConnect
from psycopg import Connection
from psycopg.rows import class_row
from pydantic import BaseModel


class ColumnDefinition(BaseModel):
    column_name: str
    data_type: str
    is_nullable: str


class ForeignKeyConstraint(BaseModel):
    table_schema: str
    table_name: str
    column_name: str
    foreign_table_schema: str
    foreign_table_name: str
    foreign_column_name: str

    def src_path(self) -> str:
        return f"{self.table_schema}.{self.table_name}.{self.column_name}"

    def ref_path(self) -> str:
        return f"{self.foreign_table_schema}.{self.foreign_table_name}.{self.foreign_column_name}"


class PgService:
    def __init__(self, db: PgConnect, student: str) -> None:
        self._db = db
        self._student = student

    def ping(self) -> bool:
        try:
            with self._db.connection() as _:
                return True
        except Exception:
            return False

    def init_schemas(self) -> Dict[str, str]:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE SCHEMA IF NOT EXISTS stg;
                    CREATE SCHEMA IF NOT EXISTS dds;
                    CREATE SCHEMA IF NOT EXISTS cdm;
                """)

                conn.commit()

        return {
            "result_key": "jatHQd&khR4C@%j@cU",
            "message": "Схемы заведены"
        }

    def check_schema_cdm(self) -> Dict[str, str]:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name='cdm';
                """)
                result = cur.fetchone()

        if result:
            return {
                "result_key": "Qt1sKKhQ}myeR2sxz@",
                "message": "Схема готова. Переходим к созданию таблиц."
            }

        return {
            "message": "Схема cdm отсутствует."
        }

    def check_table_and_index(
        self,
        table_name: str,
        table_schema: str,
        auth_columns: List[ColumnDefinition],
        auth_indexes: Dict[str, str],
        result_key,
        tup,
        auth_fk: Optional[List[ForeignKeyConstraint]] = None
    ) -> Dict[str, str]:
        with self._db.connection() as conn:
            err_msg = self._check_columns(conn, table_schema, table_name, auth_columns)
            if err_msg:
                return {
                    "message": err_msg
                }

            err_msg = self._check_foreign_keys(conn, table_schema, table_name, auth_fk)
            if err_msg:
                return {
                    "message": err_msg
                }

        # AY: Так нельзя сравнивать индексы. Нужен парсинг.
        #    cur.execute(f"""
        #            SELECT
        #                indexname,
        #                indexdef
        #            FROM pg_indexes
        #            WHERE tablename = '{table_name}'
        #            AND schemaname = '{table_schema}';
        #        """)
        #    result_index = cur.fetchall()

        # for rez in result_index:
        #     if rez[0] not in auth_indexes:
        #         return {
        #             "message": f'Обнаружено лишнее ограничение `{rez[0]}`'
        #         }
        #     if rez[1] != auth_indexes[rez[0]]:
        #         return {
        #             "message": f'Проверьте ограничение {rez[0]}.\n{auth_indexes[rez[0]]} != {rez[1]}'
        #         }

        return {
            "result_key": result_key,
            "message": tup
        }

    def _check_columns(self,
                       conn: Connection,
                       schema: str,
                       table: str,
                       auth_columns: List[ColumnDefinition]
                       ) -> Optional[str]:
        with conn.cursor(row_factory=class_row(ColumnDefinition)) as cur:
            cur.execute(
                """
                    SELECT
                        column_name,
                        data_type,
                        is_nullable
                    FROM information_schema.columns
                    WHERE
                        table_name = %(table)s
                        AND table_schema = %(schema)s;
                """,
                {
                    "table": table,
                    "schema": schema
                })
            result = cur.fetchall()

        if not result:
            return f"Таблица {table} в схеме {schema} отсутствует."

        if len(auth_columns) != len(result):
            return f"В таблице {schema}.{table} ожидается {len(auth_columns)} колонок."

        for auth_column in auth_columns:
            rez_column = next((x for x in result if x.column_name == auth_column.column_name), None)

            if not rez_column:
                return f'В таблице {schema}.{table} не обнаружено поле {auth_column.column_name}.'

            if auth_column.data_type != rez_column.data_type:
                return f'Проверьте тип поля {rez_column.column_name}. Должен быть: {auth_column.data_type}, у вас  {rez_column.data_type}'  # noqa

            if rez_column.is_nullable != auth_column.is_nullable:
                return f'Для поля {rez_column.column_name} ожидается ограничение nullable: {auth_column.is_nullable}'

    def _check_foreign_keys(self,
                            conn: Connection,
                            table_schema: str,
                            table_name: str,
                            auth_fks: Optional[List[ForeignKeyConstraint]]
                            ) -> Optional[str]:

        if not auth_fks:
            return None

        with conn.cursor(row_factory=class_row(ForeignKeyConstraint)) as cur:
            cur.execute(
                """
                    SELECT
                        tc.table_schema     AS table_schema,
                        tc.table_name       AS table_name,
                        kcu.column_name     AS column_name,
                        ccu.table_schema    AS foreign_table_schema,
                        ccu.table_name      AS foreign_table_name,
                        ccu.column_name     AS foreign_column_name
                    FROM
                        information_schema.table_constraints AS tc
                            INNER JOIN information_schema.key_column_usage AS kcu
                                ON tc.constraint_name = kcu.constraint_name
                                AND tc.table_schema = kcu.table_schema
                            INNER JOIN information_schema.constraint_column_usage AS ccu
                                ON ccu.constraint_name = tc.constraint_name
                                AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name=%(table_name)s;
                """,
                {
                    "table_name": table_name
                })
            result_fks = cur.fetchall()

        if not result_fks:
            return f"В таблице {table_schema}.{table_name} не найдены внешние ключи."

        for expected_fk in auth_fks:
            res_fk = next((x for x in result_fks if x.src_path() == expected_fk.src_path()), None)
            if not res_fk:
                return f"В таблица {table_schema}.{table_name} отсутствует внешний ключ на колонке {expected_fk.column_name}."

            if (expected_fk.ref_path() != res_fk.ref_path()):
                return f"""
                    В таблице {table_schema}.{table_name} внешний ключ указывает на {res_fk.ref_path()}.
                    А должен указывать на {expected_fk.ref_path()}.
                """
