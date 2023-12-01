import time
from pathlib import Path

import config
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
from src.extract import extract
from src.load import load
from src.transform import transform
from utils.db_connections import (close_connections, get_min_max_state,
                                  setup_connections)
from utils.logger import logger


def main():
    # root
    BASE_DIR = Path(__file__).resolve().parent
    # path to environment variables
    PATH_TO_ENV = BASE_DIR / '.env.dev'
    # load environment variables
    load_dotenv(PATH_TO_ENV)

    # setting connections to
    #   1. postgres
    #   2. elasticsearch
    #   3. redis
    # getting current state of etl
    postgres_conn, es_conn, redis_conn, state = setup_connections()
    # postgres cursor from connection
    postgres_cur = postgres_conn.cursor(cursor_factory=DictCursor)
    # min and max dates from postgres
    min_state, max_state = get_min_max_state(postgres_cur)
    # getting current state
    current_state = state.get_state('updated_at')
    try:
        # setting state if not defiend
        if current_state is None:
            state.set_state(config.REDIS_STATE, max_state)
            current_state = state.get_state(config.REDIS_STATE)
            close_connections(postgres_cur, es_conn)
            logger.info('Index was created ...')
            return current_state, min_state
        # run etl if elasticsearch index is not updated
        elif current_state != min_state:
            # extract filmwork, persons for filmwork, genres for filmwork
            # convert to pd.DataFrame
            df, df_fwg, df_fwp = extract(postgres_cur, current_state)
            # if extraction executed unsuccessfully
            if df is None:
                close_connections(postgres_cur, es_conn)
                logger.info('Index cant be updated ...')
                return current_state, min_state
            # if its ok
            else:
                data, updated_at = transform(df, df_fwg, df_fwp)
                load(data, es_conn, state, updated_at)
                close_connections(postgres_cur, es_conn)
                logger.info('Index was updated ...')
                return current_state, min_state
        # exit if elasticsearch index is updated
        else:
            close_connections(postgres_cur, es_conn)
            logger.info('Index is up to date ...')
            return current_state, min_state
    except Exception as error:
        close_connections(postgres_cur, es_conn)
        logger.error(error)
        pass
    # close postgres connection
    finally:
        close_connections(postgres_cur, es_conn)
        logger.info('Closing postgres connection ...')


if __name__ == '__main__':
    ITER = 1
    while True:
        current_state, min_state = main()
        logger.info(f'ITERATION {ITER}: current_state={current_state}, min_state={min_state}')
        ITER += 1
        time.sleep(config.SLEEP)
