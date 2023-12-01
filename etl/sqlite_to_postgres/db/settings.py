import os
from pathlib import Path

from dotenv import load_dotenv

# корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent
# загрузка переенных окружения
load_dotenv(BASE_DIR / '.env.dev')
# подключение к постгрес БД
DSL = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
}
# таблицы
TABLES = ('person', 'genre', 'filmwork', 'filmwork_genre', 'filmwork_person')
