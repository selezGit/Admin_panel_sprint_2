"""Модуль описания данных"""
import uuid
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class Genre:
    name: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    description_genre: str = field(default='')
    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class FilmworkGenre:
    filmwork_id: uuid.UUID
    genre_id: uuid.UUID


@dataclass
class Person:
    first_name: str
    last_name: str = field(default='')
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    birth_date: datetime = field(default_factory=datetime.now)
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class FilmworkPerson:
    filmwork_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    filmwork_person_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Filmwork:
    old_id: str
    title: str
    file_path: str = field(default='')
    restricted: int = field(default=0)
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    creation_date: datetime = field(default_factory=datetime.now)
    genres: List[FilmworkGenre] = field(default_factory=list)
    persons: List[FilmworkPerson] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    description: str = field(default='')
    rating: float = field(default=0.0)
    type: str = field(default='movie')
