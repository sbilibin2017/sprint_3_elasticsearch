'''Валидация данных.'''

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.constants import EMPTY_STRING, NEW_UUID, NOW, TYPE_DEFAULT


@dataclass
class TimeStampedMixin:
    '''Класс для представления дат.'''

    created_at: datetime = field(default=NOW)
    updated_at: datetime = field(default=NOW)


@dataclass
class UUIDMixin:
    '''Класс для хэш-идентификатора/'''

    id: uuid.UUID = field(default_factory=NEW_UUID)


@dataclass
class Person(UUIDMixin, TimeStampedMixin):
    '''Класс для представления персоны.'''

    full_name: str = field(default=EMPTY_STRING)


@dataclass
class Genre(UUIDMixin, TimeStampedMixin):
    '''Класс для представления жанра.'''

    name: str = field(default=EMPTY_STRING)
    description: str = field(default=EMPTY_STRING)


@dataclass
class Filmwork(UUIDMixin, TimeStampedMixin):
    '''Класс для представления кинопроизведения.'''

    title: str = field(default=EMPTY_STRING)
    description: str = field(default=EMPTY_STRING)
    creation_date: datetime = field(default=None)
    file_path: str = field(default=EMPTY_STRING)
    rating: float = field(default=None)
    type: str = field(default=TYPE_DEFAULT)


@dataclass
class FilmworkGenre(UUIDMixin):
    '''Класс для представления жанра кинопроизведения.'''

    id: uuid.UUID = field(default_factory=NEW_UUID)
    filmwork_id: uuid.UUID = field(default_factory=NEW_UUID)
    genre_id: uuid.UUID = field(default_factory=NEW_UUID)
    created_at: datetime = field(default=NOW)


@dataclass
class FilmworkPerson(UUIDMixin):
    'Класс для представления персоны кинопроизведения.'
    role: str = field(default=TYPE_DEFAULT)
    filmwork_id: uuid.UUID = field(default_factory=NEW_UUID)
    person_id: uuid.UUID = field(default_factory=NEW_UUID)
    created_at: datetime = field(default=NOW)
