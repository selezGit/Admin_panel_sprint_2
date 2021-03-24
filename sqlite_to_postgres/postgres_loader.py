"""Модуль загузки данных в Postgresql."""


import logging
from dataclasses import asdict

import psycopg2.extras
from psycopg2.extensions import connection as _connection

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    encoding='utf-8', level=logging.INFO)


class PostgresSaver:
    """Класс загрузки данных."""
    SAVE_PERSON_QUERY = """
                        WITH ins1 AS
                        (INSERT INTO public.movie_admin_filmwork (id, old_id, title, description, rating, RESTRICTED, creation_date, created, modified, file_path, TYPE)
                        VALUES (%(filmwork_id)s,
                                %(old_id)s,
                                %(title)s,
                                %(description)s,
                                %(rating)s,
                                %(restricted)s,
                                %(creation_date)s,
                                %(created)s,
                                %(modified)s,
                                %(file_path)s,
                                %(type)s) ON CONFLICT ON CONSTRAINT movie_admin_filmwork_old_id_key DO UPDATE
                        SET old_id=EXCLUDED.old_id RETURNING id AS film_work_id),
                            ins2 AS
                        (INSERT INTO public.movie_admin_person (id, first_name, last_name, birth_date, created, modified)
                        VALUES (%(person_id)s,
                                %(first_name)s,
                                %(last_name)s,
                                %(birth_date)s,
                                %(created)s,
                                %(modified)s) ON CONFLICT ON CONSTRAINT person_name_uq DO UPDATE
                        SET first_name=EXCLUDED.first_name,
                            last_name=EXCLUDED.last_name,
                            birth_date=EXCLUDED.birth_date RETURNING id AS person_id)
                        INSERT INTO public.movie_admin_filmworkperson (id, filmwork_id, person_id, ROLE)
                        SELECT %(filmwork_person_id)s,
                            ins1.film_work_id,
                            ins2.person_id,
                            %(role)s
                        FROM ins1,
                            ins2 ON CONFLICT ON CONSTRAINT person_film_work_uq DO NOTHING
                        """
    SAVE_GENRE_QUERY = """
                        WITH ins1 AS
                        (INSERT INTO public.movie_admin_filmwork (id, old_id, title, description, rating, RESTRICTED, creation_date, created, modified, file_path, TYPE)
                        VALUES (%(filmwork_id)s,
                                %(old_id)s,
                                %(title)s,
                                %(description)s,
                                %(rating)s,
                                %(restricted)s,
                                %(creation_date)s,
                                %(created)s,
                                %(modified)s,
                                %(file_path)s,
                                %(type)s) ON CONFLICT ON CONSTRAINT movie_admin_filmwork_old_id_key DO UPDATE
                        SET old_id = EXCLUDED.old_id RETURNING id AS film_work_id),
                            ins3 AS
                        (INSERT INTO public.movie_admin_genre (id, name, description, created, modified)
                        VALUES (%(genre_id)s,
                                %(name)s,
                                %(description_genre)s,
                                %(created)s,
                                %(modified)s) ON CONFLICT ON CONSTRAINT movie_admin_genre_name_key DO UPDATE
                        SET name = EXCLUDED.name RETURNING id AS genre_id)
                        INSERT INTO public.movie_admin_filmwork_genres (filmwork_id, genre_id)
                        SELECT ins1.film_work_id,
                            ins3.genre_id
                        FROM ins1,
                            ins3 ON CONFLICT ON CONSTRAINT movie_admin_filmwork_genres_filmwork_id_genre_id_6e093fa3_uniq DO NOTHING
                        """

    def __init__(self, pg_conn: _connection):
        self.pg_conn = pg_conn
        self.pg_cur = pg_conn.cursor()
        psycopg2.extras.register_uuid()

    def save_all_data(self, data):
        """Функция вставки данных."""
        for film, persons, genres in data:
            for person, movie_person in zip(persons, film.persons):
                self.pg_cur.execute(self.SAVE_PERSON_QUERY, ({**asdict(film),
                                                              **asdict(movie_person),
                                                              **asdict(person)}))
            for genre, movie_genre in zip(genres, film.genres):
                self.pg_cur.execute(self.SAVE_GENRE_QUERY, ({**asdict(film),
                                                             **asdict(movie_genre),
                                                             **asdict(genre)}))

        self.pg_conn.commit()
        logging.info('Message: Successfully loaded %d films', len(data))
