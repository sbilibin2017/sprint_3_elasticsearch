from datetime import datetime

import config
import pandas as pd
import psycopg2
import pydantic
from utils.logger import logger
from utils.validators import (FilmworkGenrePydantic, FilmworkPersonPydantic,
                              FilmworkPydantic)


def get_filmwork_query(FilmworkPydantic: pydantic.BaseModel) -> tuple[str, datetime]:
    '''Creates filmwork query with respect of current etl state.'''
    keys = ','.join(list(FilmworkPydantic.__fields__))
    query = f"""
                SELECT {keys}
                FROM filmwork
                WHERE updated_at <= %s
                ORDER BY updated_at DESC
            """
    return query


def get_filmwork_4idxs(FilmworkPydantic: pydantic.BaseModel, chunk: list[dict]) -> pd.DataFrame:
    '''Creatres dataframe for filmwork.'''
    columns = list(FilmworkPydantic.__fields__)
    df = pd.DataFrame.from_records(chunk, columns=columns)
    return df


def get_filmwork_genre_4idxs(
    FilmworkGenrePydantic, cursor: psycopg2.extensions.cursor, df: pd.DataFrame
) -> pd.DataFrame:
    '''Creatres dataframe for filmwork genres.'''
    columns = list(FilmworkGenrePydantic.__fields__)
    keys = ','.join(columns)
    filwork_idxs = tuple(df['id'].values.tolist())
    wc = ','.join(['%s' for _ in range(len(filwork_idxs))])
    query = f"""
                SELECT {keys}
                FROM filmwork_genre fwg
                LEFT JOIN genre g
                    ON fwg.genre_id = g.id
                WHERE filmwork_id in ({wc})
            """
    cursor.execute(query, filwork_idxs)
    df = pd.DataFrame.from_records(cursor.fetchall(), columns=columns).rename(columns={'filmwork_id': 'id'})
    return df


def get_filmwork_person_4idxs(FilmworkPersonPydantic: pydantic.BaseModel, cursor: psycopg2.extensions.cursor, df):
    '''Creatres dataframe for filmwork persons.'''
    columns = list(FilmworkPersonPydantic.__fields__)
    keys = ','.join(columns)
    filwork_idxs = tuple(df['id'].values.tolist())
    wc = ','.join(['%s' for _ in range(len(filwork_idxs))])
    query = f"""
                SELECT {keys}
                FROM filmwork_person fwp
                    LEFT JOIN person p
                    ON fwp.person_id = p.id
                WHERE filmwork_id in ({wc})
            """
    cursor.execute(query, filwork_idxs)
    df = pd.DataFrame.from_records(cursor.fetchall(), columns=columns).rename(
        columns={'full_name': 'name', 'filmwork_id': 'id'}
    )
    return df


def get_dataframes(cursor: psycopg2.extensions.cursor, chunk: int) -> tuple[pd.DataFrame]:
    df = get_filmwork_4idxs(FilmworkPydantic, chunk)
    # dataframe with filmwork and genres
    df_fwg = get_filmwork_genre_4idxs(FilmworkGenrePydantic, cursor, df)
    # dataframe with filmwork and persons
    df_fwp = get_filmwork_person_4idxs(FilmworkPersonPydantic, cursor, df)
    return df, df_fwg, df_fwp


def extract(postgres_cur: psycopg2.extensions.cursor, current_state: datetime) -> tuple[dict]:
    '''Extracts data from postgres.'''
    logger.info('\t[EXTRACT] getting current state ...')
    # getting  query for new filmwork chunk
    query = get_filmwork_query(FilmworkPydantic)
    try:
        logger.info(f'\t[EXTRACT] current_state:{current_state}')
        # execute query
        postgres_cur.execute(query, (current_state,))
        # getting chunk of data
        chunk = postgres_cur.fetchmany(config.POSTGRES_CHUNK_SIZE)
        # transform filmwork with genres, persons to dataframe
        df, df_fwg, df_fwp = get_dataframes(postgres_cur, chunk)
        return df, df_fwg, df_fwp
    except psycopg2.OperationalError:
        logger.info('cant connect to postgres ...')
        return None, None, None
