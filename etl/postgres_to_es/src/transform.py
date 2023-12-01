import uuid
from datetime import datetime

import pandas as pd

from utils.logger import logger
from utils.validators import IndexData


def build_es_data(
    filmwork_id: uuid.UUID, df: pd.DataFrame, df_fwg: pd.DataFrame, df_fwp: pd.DataFrame
) -> tuple[dict, datetime]:
    '''Prepare json data.'''

    DEFAULT_NUM = -1.0
    DEFAULT_STR = ''
    DEFAULT_LIST = ['']

    df['rating'].fillna(DEFAULT_NUM, inplace=True)
    df_sub = df[df['id'] == filmwork_id]
    df_fwg_sub = df_fwg[df_fwg['id'] == filmwork_id]
    df_fwp_sub = df_fwp[df_fwp['id'] == filmwork_id]

    d = {}
    d['id'] = filmwork_id
    d['imdb_rating'] = df_sub['rating'].iloc[0]
    d['genre'] = df_fwg_sub['name'].unique().tolist()
    d['title'] = df_sub['title'].iloc[0] or DEFAULT_STR
    d['description'] = df_sub['description'].iloc[0] or DEFAULT_STR
    subdf_dir = df_fwp_sub[df_fwp_sub['role'] == 'director']
    if len(subdf_dir) > 0:
        d['director'] = subdf_dir['name'].iloc[0]
    else:
        d['director'] = DEFAULT_STR
    for key in ['actor', 'writer']:
        subdf = df_fwp_sub[df_fwp_sub['role'] == key]
        if len(subdf) > 0:
            d[f'{key}s_names'] = subdf['name'].values.tolist()
            d[f'{key}s'] = subdf[['id', 'name']].to_dict('records')
        else:
            d[f'{key}s_names'] = DEFAULT_LIST
            d[f'{key}s'] = DEFAULT_LIST

    d_validated = IndexData(**d).dict()

    return d_validated, df_sub['updated_at'].iloc[0]


def transform(df: pd.DataFrame, df_fwg: pd.DataFrame, df_fwp: pd.DataFrame) -> tuple[list[dict], datetime]:
    '''Transforms extracted data.'''
    data = []
    for filmwork_id in df['id'].values:
        row, updated_at = build_es_data(filmwork_id, df, df_fwg, df_fwp)
        data.append(row)
        logger.info(f'\t[TRANSFORM] row:{row}')
    return data, updated_at
