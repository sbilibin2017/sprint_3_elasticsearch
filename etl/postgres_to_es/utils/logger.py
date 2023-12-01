'''Логгер.'''

import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(
    encoding='utf-8',
    format='%(asctime)s %(message)s',
    level=logging.DEBUG,
    handlers=[logging.FileHandler(BASE_DIR / 'postgres_to_es.log', mode='w'), logging.StreamHandler()],
)
logger = logging.getLogger('postgres_to_es')
