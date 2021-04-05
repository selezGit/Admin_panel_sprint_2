from typing import Coroutine, Generator

from .decorators import init_generator


@init_generator
def transform(next_coroutine: Coroutine) -> Generator:
    """Функция трансформации данных"""
    try:
        unique_filter = []
        while True:
            data = (yield)
            result = []
            for row in data:
                id, title, description, rating, type, persons, genres = row

                if id in unique_filter:
                    continue
                unique_filter.append(id)

                writers = [{'id': id, 'name': name} for id, name, role in [
                    person.split(';') for person in persons if person] if role == 'writer']
                actors = [{'id': id, 'name': name} for id, name, role in [
                    person.split(';') for person in persons if person] if role == 'actor']
                directors = [{'id': id, 'name': name} for id, name, role in [
                    person.split(';') for person in persons if person] if role == 'director']

                result.append({'id': id,
                            'genre': genres,
                            'writers': writers,
                            'actors': actors,
                            'directors': directors,
                            'writers_names': [name.get('name') for name in writers],
                            'actors_names': [name.get('name') for name in actors],
                            'directors_names': [name.get('name') for name in directors],
                            'rating': float(rating),
                            'title': title,
                            'description': description})
            next_coroutine.send(result)
    except GeneratorExit:
        next_coroutine.close()

