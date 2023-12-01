"""Тесты для панели администратора."""

import os
from contextlib import closing
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from new_admin_panel_sprint_1.sqlite_to_postgres.db.settings import DSL, TABLES
from new_admin_panel_sprint_1.sqlite_to_postgres.src.sqlite_context_manager import conn_context
from psycopg2.extras import RealDictCursor

# корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# загрузка переменных окружения
load_dotenv(BASE_DIR / '.env')


SQLITE_DB_PATH = os.path.join(BASE_DIR, 'db', os.environ.get('SQLITE_DB'))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))

#######################################################################################


def test_table_size() -> None:
    '''Тестирование размеров таблиц в sqlite и postgre БД.

    :param str db: строка с подключением к sqlite БД
    :param dict DSL: словарь с подключением к postgre БД
    '''

    def get_sqlite_count_cursor(sqlite_cur: RealDictCursor, table_name: str) -> RealDictCursor:
        '''Получение sqlite курсора с выполненным запросом.

        :param DictCursor sqlite_cur: курсор sqlite
        :param str table_name: название таблицы
        :return DictCursor: курсор sqlite с выполненным запросом
        '''
        sqlite_cur.execute(f"""SELECT count(*) as  count FROM {table_name}""")
        return sqlite_cur

    def get_sqlite_count_values(sqlite_cur: RealDictCursor) -> dict:
        '''Получение результата выполнения запроса.

        :param DictCursor sqlite_cur: курсор sqlite
        :return list: результат выполнения запроса
        '''
        return sqlite_cur.fetchone()

    def get_psql_count_cursor(pg_cur: RealDictCursor, table_name: str) -> RealDictCursor:
        '''Получение psql курсора с выполненным запросом.

        :param DictCursor pg_cur: курсор postgre
        :param str table_name: название таблицы
        :return DictCursor: курсор postgre с выполненным запросом
        '''
        pg_cur.execute(f"""SELECT count(*) as count FROM content.{table_name}""")
        return pg_cur

    def get_psql_count_values(pg_cur: RealDictCursor) -> list:
        '''Получение результата выполнения запроса.

        :param DictCursor pg_cur: курсор postgre
        :return list: результат выполнения запроса
        '''
        return pg_cur.fetchone()

    def compare_count(count_sqlite: int, count_psql: int, table_name: str) -> None:
        '''Сравнение размеров таблиц.

        :param dict count_sqlite: число записей в sqlite
        :param dict count_psql: число записей в postgre
        '''
        n1 = list(count_sqlite.values())[0]
        n2 = list(count_psql.values())[0]
        assert n1 == n2, f'{table_name} - размеры не совпадают'

    with conn_context(SQLITE_DB_PATH) as sqlite_conn, closing(
        psycopg2.connect(**DSL, cursor_factory=RealDictCursor)
    ) as pg_conn:
        sqlite_cur = sqlite_conn.cursor()
        for table_name in TABLES:
            sqlite_cur = get_sqlite_count_cursor(sqlite_cur, table_name)
            count_sqlite = get_sqlite_count_values(sqlite_cur)
            with pg_conn.cursor() as pg_cur:
                pg_cur = get_psql_count_cursor(pg_cur, table_name)
                count_psql = get_psql_count_values(pg_cur)
                compare_count(count_sqlite, count_psql, table_name)


def test_table_values() -> None:
    '''Тестирование значений таблиц в sqlite и postgre БД.

    :param str db: строка с подключением к sqlite БД
    :param dict DSL: словарь с подключением к postgre БД
    '''

    def get_sqlite_select_all(sqlite_cur: RealDictCursor, table_name: str) -> RealDictCursor:
        '''Выборка всех данных из таблицы sqlite.

        :param DictCursor sqlite_cur: курсор sqlite
        :param str table_name: название таблицы
        :return DictCursor: выполнение запроса
        '''
        return sqlite_cur.execute(f"""SELECT * FROM {table_name} ORDER BY {table_name}.id""")

    def get_sqlite_chunk(sqlite_cur: RealDictCursor) -> list:
        '''Получение результата запроса к sqlite.

        :param DictCursor sqlite_cur: курсор sqlite
        :return list: результат запроса
        '''
        return sqlite_cur.fetchmany(CHUNK_SIZE)

    def get_sqlite_idxs(sqlite_values: list) -> list:
        '''Получение id sqlite запроса.

        :param DictCursor sqlite_cur: курсор sqlite
        :return list: список id
        '''
        if sqlite_values:
            idxs = tuple([str(el['id']) for el in sqlite_values])
            return idxs
        return False

    def get_psql_values_in_chunk_with_idxs(pg_cur: RealDictCursor, table_name: str, idxs: list) -> list:
        '''Выборка всех данных из таблицы postgre.

        :param DictCursor pg_cur: курсор postgre
        :param str table_name: название таблицы
        :param list idxs: выбранные id
        :return list: результат запроса
        '''
        pg_cur.execute(
            f"""SELECT * FROM content.{table_name} \
                    WHERE content.{table_name}.id in {idxs} ORDER BY content.{table_name}.id;"""
        )
        return pg_cur.fetchmany(CHUNK_SIZE)

    def compare_values(sqlite_values: list, psql_values: list) -> None:
        '''Сравнение размера выборок и значений выборок.

        :param list[dict] sqlite_values: результат запроса к sqlite
        :param list[dict] psql_values: результат запроса к postgre
        '''
        assert len(sqlite_values) == len(psql_values)
        for i in range(len(sqlite_values)):
            id_sqlite = sqlite_values[i]['id']
            id_psql = psql_values[i]['id']
            assert id_sqlite == id_psql, f'{table_name} - значения не совпадают. {id_sqlite} <-> {id_psql}'

    with conn_context(SQLITE_DB_PATH) as sqlite_conn, closing(
        psycopg2.connect(**DSL, cursor_factory=RealDictCursor)
    ) as pg_conn:
        sqlite_cur = sqlite_conn.cursor()
        for table_name in TABLES:
            sqlite_cur = get_sqlite_select_all(sqlite_cur, table_name)
            while True:
                sqlite_values = get_sqlite_chunk(sqlite_cur)
                if sqlite_values:
                    idxs = get_sqlite_idxs(sqlite_values)
                    with pg_conn.cursor() as pg_cur:
                        psql_values = get_psql_values_in_chunk_with_idxs(pg_cur, table_name, idxs)
                        compare_values(sqlite_values, psql_values)
                else:
                    break


if __name__ == '__main__':
    test_table_size()
    test_table_values()
