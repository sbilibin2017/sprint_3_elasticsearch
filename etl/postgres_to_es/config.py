import os

# postgres
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_CHUNK_SIZE = int(os.getenv('POSTGRES_CHUNK_SIZE'))

# elasticsearch
ES_HOST = os.getenv('ES_HOST')
ES_PORT = os.getenv('ES_PORT')
ES_INDEX = os.getenv('ES_INDEX')
ES_MAPPING_FILENAME = os.getenv('ES_MAPPING_FILENAME')

# redis
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_STATE = os.getenv('REDIS_STATE')

# others
SLEEP = int(os.getenv('SLEEP'))
