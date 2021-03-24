
import datetime
import uuid
from dataclasses import asdict, dataclass
from typing import List

from django.contrib.postgres.aggregates.general import ArrayAgg
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movie_admin.models import Filmwork, PersonRoleType


@dataclass
class Movie:
    id: uuid.UUID
    title: str
    description: str
    creation_date: datetime.datetime
    rating: float
    type: PersonRoleType
    genres: List[str]
    actors: List[str]
    directors: List[str]
    writers: List[str]


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        """функция получения данных из ORM"""

        self.uuid = self.kwargs.get('pk', None)
        if self.uuid:
            queryset = self.model.objects.filter(id=self.uuid).annotate(
                person_name=ArrayAgg('persons__first_name'),
                role=ArrayAgg('filmworkperson__role'))
            return queryset

        queryset = self.model.objects.all().prefetch_related('persons', 'genres').annotate(
            person_name=ArrayAgg('persons__first_name'),
            role=ArrayAgg('filmworkperson__role'))

        return queryset

    def render_to_response(self, context):
        """функция отдаёт ответ на api запрос"""
        return JsonResponse(context)

    def dict_serializator(self, movie):
        """сериализатор фильмов"""
        persons = [{'name': name, 'role': role}
                   for name, role in zip(movie.person_name, movie.role) if name]
        data = Movie(movie.id,
                     movie.title,
                     movie.description,
                     movie.creation_date,
                     movie.rating,
                     movie.type,
                     [genre.name for genre in movie.genres.all()],
                     [person['name'] for person in persons if person['role'] == 'actor'],
                     [person['name'] for person in persons if person['role'] == 'director'],
                     [person['name'] for person in persons if person['role'] == 'writer'])

        return asdict(data)


class MoviesListApi(MoviesApiMixin, BaseListView):
    """Возвращает данные по всем фильмам"""
    paginate_by = 50

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        page_size = self.get_paginate_by(queryset)

        paginator, page, queryset, _ = self.paginate_queryset(
            queryset,
            page_size
        )
        result = [self.dict_serializator(movie)
                  for movie in paginator.page(page.number)]

        context = {'count': paginator.count,
                   'total_pages': paginator.num_pages,
                   'prev': page.previous_page_number() if page.has_previous() else None,
                   'next': page.next_page_number() if page.has_next() else None,
                   'results': result
                   }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """Возвращает данные по одному фильму"""

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()

        for movie in queryset:
            context = self.dict_serializator(movie)
        return context
