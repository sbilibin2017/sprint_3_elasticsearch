import json
from datetime import datetime
from http import HTTPStatus
from pathlib import Path

import backoff
import config
import elasticsearch
import psycopg2
import pydantic
import redis
from elasticsearch import Elasticsearch
from utils.logger import logger
from utils.state import State
from utils.validators import EsPydantic, PostgresPydantic, RedisPydantic

BASE_DIR = Path(__file__).resolve().parent.parent


@backoff.on_exception(backoff.expo, psycopg2.OperationalError, max_tries=5)
def get_postgres_conn(PostgresConfig: pydantic.BaseModel) -> psycopg2.connect:
    '''Get postgres params.'''
    d = {
        'dbname': config.POSTGRES_DB,
        'user': config.POSTGRES_USER,
        'password': config.POSTGRES_PASSWORD,
        'host': config.POSTGRES_HOST,
        'port': config.POSTGRES_PORT,
    }
    d = PostgresPydantic(**d).dict()
    try:
        return psycopg2.connect(**d)
    except psycopg2.OperationalError as error:
        logger.error(error)


@backoff.on_exception(backoff.expo, elasticsearch.ConnectionError, max_tries=5)
def get_es_conn(EsPydantic: pydantic.BaseModel) -> Elasticsearch:
    '''Get elasticsearch instance.'''
    d = {'host': config.ES_HOST, 'port': config.ES_PORT}
    d = EsPydantic(**d).dict()
    try:
        return Elasticsearch(retry_on_timeout=True, **d)
    except elasticsearch.ConnectionError as error:
        logger.error(error)


@backoff.on_exception(backoff.expo, redis.ConnectionError, max_tries=5)
def get_redis_conn(RedisPydantic: pydantic.BaseModel) -> redis.Redis.client:
    '''Get redis instance.'''
    d = {'host': config.REDIS_HOST, 'port': config.REDIS_PORT}
    d = RedisPydantic(**d).dict()
    pool = redis.ConnectionPool(**d)
    try:
        return redis.Redis(connection_pool=pool)
    except redis.ConnectionError as error:
        logger.error(error)


def set_es_index(es_cur: Elasticsearch) -> Elasticsearch:
    '''Set elasticsearch index.'''
    with open(BASE_DIR / config.ES_MAPPING_FILENAME, 'r') as f:
        mapping = json.load(f)
    indices = es_cur.indices.get_alias().keys()
    if config.ES_INDEX not in indices:
        es_cur.indices.create(index=config.ES_INDEX, ignore=HTTPStatus.BAD_REQUEST, body=mapping)
        logger.error('Creating es ondex ...')
    es_cur.indices.get_mapping(config.ES_INDEX)
    logger.error('Getting es ondex ...')
    return es_cur


def setup_connections() -> list[psycopg2.connect, Elasticsearch, redis.Redis.client, State]:
    '''Set connections to postgres, redis, elasticsearch, init state.'''
    postgres_conn = get_postgres_conn(PostgresPydantic)
    es_conn = set_es_index(get_es_conn(EsPydantic))
    redis_conn = get_redis_conn(RedisPydantic)
    state = State(redis_conn)
    logger.info('Connections were set successfully ...')
    return postgres_conn, es_conn, redis_conn, state


def get_min_max_state(postgres_cur: psycopg2.extensions.cursor) -> tuple[datetime]:
    '''Get min and max date from postgres.'''
    postgres_cur.execute("""SELECT min(updated_at) FROM filmwork""")
    min_state = postgres_cur.fetchall()[0][0]
    postgres_cur.execute("""SELECT max(updated_at) FROM filmwork""")
    max_state = postgres_cur.fetchall()[0][0]
    logger.info('Getting min and max state ...')
    return min_state, max_state


def close_connections(postgres_cur, es_conn):
    postgres_cur.close()
    es_conn.transport.close()
