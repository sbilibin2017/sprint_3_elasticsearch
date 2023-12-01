'''Главный модуль.'''

import os
from contextlib import closing
from pathlib import Path

import psycopg2
from db.settings import DSL
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from src.load_from_sqlite import load_from_sqlite
from src.logger import logger
from src.sqlite_context_manager import conn_context

# корень проекта
BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
# загрузка переенных окружения
load_dotenv(BASE_DIR / '.env.dev')
# путь до sqlite БД
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'db', os.getenv('SQLITE_DB'))

if __name__ == '__main__':
    logger.info('Открываем соединения с sqlite и postgre ...')
    with conn_context(SQLITE_DB_PATH) as sqlite_conn, closing(
        psycopg2.connect(**DSL, cursor_factory=RealDictCursor)
    ) as pg_conn:
        sqlite_cur = sqlite_conn.cursor()
        load_from_sqlite(sqlite_conn, pg_conn)
    logger.info('Закрываем соединения с sqlite и postgre ...')
