from datetime import datetime

from pydantic import BaseModel


class PostgresPydantic(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int


class EsPydantic(BaseModel):
    host: str
    port: int


class RedisPydantic(BaseModel):
    host: str
    port: int


class IndexData(BaseModel):
    id: str
    imdb_rating: float
    genre: list[str]
    title: str
    description: str
    director: str
    actors_names: list[str]
    actors: list[dict]
    writers_names: list[str]
    writers: list[dict]


class FilmworkPydantic(BaseModel):
    id: str
    rating: float
    title: str
    description: str
    updated_at: datetime


class FilmworkGenrePydantic(BaseModel):
    filmwork_id: str
    genre_id: str
    name: str
    description: str


class FilmworkPersonPydantic(BaseModel):
    filmwork_id: str
    person_id: str
    full_name: str
    role: str
