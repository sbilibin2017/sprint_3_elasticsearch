from datetime import datetime

import config
import elasticsearch
from elasticsearch import helpers
from utils.logger import logger
from utils.state import State


def collect_actions(data: list[dict]) -> list[dict]:
    '''Prepare data to adding to elasticsearch index.'''
    actions = []
    for row in data:
        action = {"_index": config.ES_INDEX, "_type": "_doc", "_id": row['id'], "_source": row}
        actions.append(action)
        logger.info(f'\t[LOAD] action:{row}')
    return actions


def load(data: list[dict], es_conn: elasticsearch.client, state: State, updated_at: datetime) -> None:
    '''Loads transformed data to elasticsearch index.'''
    helpers.bulk(es_conn, collect_actions(data))
    new_updated_at = updated_at
    state.set_state(config.REDIS_STATE, new_updated_at)
    logger.info(f'\t[LOAD] new_updated_at:{new_updated_at}')
