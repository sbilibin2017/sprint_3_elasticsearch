'''Проверка идентичности sqlite3 м postgre БД.'''

import os
import sqlite3
from dataclasses import asdict
from typing import Generator

import psycopg2
from db.settings import TABLES
from psycopg2.extras import RealDictCursor
from src.logger import logger
from src.validators import Filmwork, FilmworkGenre, FilmworkPerson, Genre, Person


class SQLiteExtractor:
    '''Класс для извлечения данных из sqlite3 БД.'''

    def __init__(self, conn: sqlite3.Connection):
        # подключение к sqlite
        self.sql_conn = conn.cursor()
        # названия таблиц
        self.table_name = TABLES

    def extract_movies(self):
        '''Извлекает данные из таблицы.'''
        # для каждой таблицы
        for table_name in self.table_name:
            # выбираем данные
            self.sql_conn.execute(f'''SELECT * FROM {table_name}''')
            # пока в результате запроса есть данные
            while True:
                # отдаем данные чанками по 1000 записей
                rows = self.sql_conn.fetchmany(int(os.environ.get('CHUNK_SIZE')))
                if rows:
                    yield (table_name, rows)
                else:
                    break


class PostgresSaver:
    '''Класс для загрузки данных в postre БД.'''

    def __init__(self, psql_conn: RealDictCursor) -> None:
        # подключение к postgre
        self.psql_conn = psql_conn
        # датаклассы для валидации
        self.dataclasses = dict(zip(TABLES, (Person, Genre, Filmwork, FilmworkGenre, FilmworkPerson)))
        # счетчик записей в таблицах
        self.row_counters = dict(zip(TABLES, [0] * len(TABLES)))

    def insert_query(self, table_name: str, row: list) -> None:
        '''Вставляет данные в таблицу.'''
        # список ключей
        cols = ','.join(row[0].keys())
        # метки для запроса
        qmarks = ','.join(['%s' for s in row[0].keys()])
        # значения
        values = tuple([tuple(r.values()) for r in row])

        # запрос для вставки данных в БД
        insert_statement = f'INSERT INTO content.{table_name} \
            ({cols}) VALUES ({qmarks}) ON CONFLICT DO NOTHING;'

        with self.psql_conn.cursor() as cur:
            try:
                cur.executemany(insert_statement, values)
                self.psql_conn.commit()
            except psycopg2.Error as error:
                logger.exception(error)

    def validate(self, model, data):
        '''Валидирует данные.'''
        return asdict(model(**data))

    def save_all_data(self, gen: Generator) -> None:
        '''Валидирует данные и вставляет их в БД.'''
        for tup in gen:
            # таблица, данные
            table_name, rows = tup
            logger.info(f'Таблица: {table_name}')
            # # для каждой строки в данных
            # for row in rows:
            # валидируем данные
            rows_validated = [self.validate(self.dataclasses[table_name], row) for row in rows]

            # вставляем данные в постргрес БД
            self.insert_query(table_name=table_name, row=rows_validated)
            # увеличиваем счетчик строк
            self.row_counters[table_name] += len(rows_validated)
            logger.info(f'Число строк в таблицах: {self.row_counters}')
