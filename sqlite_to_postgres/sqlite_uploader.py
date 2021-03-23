"""Модуль выгрузки данных из SQLite."""


import sqlite3

from model import Filmwork, Genre, FilmworkGenre, FilmworkPerson, Person


class SQLiteLoader:
    """Класс выгрузки данных."""
    LOAD_DATA_QUERY = """
            WITH json_writers
                AS (SELECT movies.id,
                            Group_concat(DISTINCT value)  AS writers,
                            Group_concat(DISTINCT w.NAME) AS NAME
                    FROM   movies,
                            Json_tree(writers)
                            INNER JOIN writers w
                                    ON value = w.id
                    WHERE  NOT writers = ''
                    GROUP  BY movies.id),
                one_writer
                AS (SELECT m.id,
                            m.writer,
                            w.NAME
                    FROM   movies m
                            LEFT JOIN writers w
                                ON m.writer = w.id
                    WHERE  NOT m.writer = ''),
                all_writers
                AS (SELECT *
                    FROM   one_writer
                    UNION
                    SELECT *
                    FROM   json_writers)
            SELECT DISTINCT m.id,
                            title,
                            plot,
                            imdb_rating,
                            genre,
                            Group_concat(DISTINCT a.NAME),
                            director,
                            aw.NAME
            FROM   movies m
                INNER JOIN movie_actors ma
                        ON m.id = ma.movie_id
                INNER JOIN actors a
                        ON ma.actor_id = a.id
                INNER JOIN all_writers aw
                        ON m.id = aw.id
            GROUP  BY m.id
            """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def load_movies(self) -> list:
        """Загружает всю информацию из старой базы, передаёт обработчику
        по одной строке, результат записывает в список."""

        data = self.connection.execute(self.LOAD_DATA_QUERY).fetchall()
        valid_data = [self.data_processor(row) for row in data]

        return valid_data

    def data_processor(self, row: tuple) -> Filmwork:
        """Функция обработки данных, на вход получает строку,
         возвращает инстанс датакласса Filmwork"""
        old_id, title, plot, imdb_rating, genres, actors, directors, writers = row

        plot = plot if plot != 'N/A' else ''
        imdb_rating = imdb_rating if imdb_rating != 'N/A' else 0

        # create movie
        movie = Filmwork(old_id=old_id,
                      title=title,
                      description=plot,
                      rating=imdb_rating)

        # append to foreignkey tables
        genres = [Genre(name=name.strip()) for name in genres.split(',')]
        actors = [Person(first_name=name.strip())
                  for name in actors.split(',') if name != 'N/A']
        directors = [Person(first_name=name.strip())
                     for name in directors.split(',') if name != 'N/A']
        writers = [Person(first_name=name.strip())
                   for name in writers.split(',') if name != 'N/A']

        persons = actors + directors + writers

        # append to M2M tables
        filmwork_genres = [FilmworkGenre(movie.id, genre.genre_id) for genre in genres]
        filmwork_person_actors = [FilmworkPerson(
            movie.id, person.person_id, role='actor') for person in actors]
        filmwork_person_directors = [FilmworkPerson(
            movie.id, person.person_id, role='director') for person in directors]
        filmwork_person_writers = [FilmworkPerson(
            movie.id, person.person_id, role='writer') for person in writers]

        # add M2M to movie
        movie.genres = filmwork_genres
        movie_persons = filmwork_person_actors + filmwork_person_directors + filmwork_person_writers
        movie.persons = movie_persons

        return movie, persons, genres
