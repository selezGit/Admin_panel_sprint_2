from datetime import datetime
from typing import Any, Coroutine, Generator

import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from redis import Redis

from . import logger
from .decorators import backoff, init_generator
from .storage import RedisStorage, State

DSL = {'dbname': 'movie_admin', 'user': 'django_admin',
       'password': 1234, 'host': 'db', 'port': 5432}

red_conn = RedisStorage(Redis(host='redis'))
state = State(red_conn)


@backoff()
def data_upload_first_stage(next_coroutine: Coroutine, table: str, check_time: datetime, limit=100) -> Any:
    """выгрузка данных первый этап:
     выгрузка данных из таблиц genre или person или film_work
    """

    while True:
        try:
            with psycopg2.connect(**DSL, cursor_factory=DictCursor) as pg_conn, pg_conn.cursor() as pg_cur:
                offset = state.get_state(key='offset_first')
                sql_query = sql.SQL('''SELECT id FROM {table}
                                    WHERE modified > {check_time}
                                    ORDER BY modified
                                    LIMIT {limit} OFFSET {offset}''').format(table=sql.Identifier('content', table),
                                                                             check_time=sql.Literal(
                    check_time),
                    limit=sql.Literal(limit),
                    offset=sql.Literal(offset))
                pg_cur.execute(sql_query)
                result = [uuid[0] for uuid in pg_cur.fetchall() if uuid]
                if not result:
                    logger.info('data not found, coroutine_1 is stoped')
                    state.set_state('offset_first', 0)
                    break

            state.set_state('offset_first', offset+limit)
            next_coroutine.send(result)

        except GeneratorExit:
            next_coroutine.close()
            break


@init_generator
@backoff()
def data_upload_second_stage(next_coroutine: Coroutine, table: str, check_time: datetime, limit=100) -> Generator:
    """выгрузка данных второй этап:
    выгрузка из m2m таблиц genre_film_work или person_film_work
    """
    try:
        column = table + '_id'
        table += '_film_work'

        while True:
            list_id = (yield)
            result = []
            with psycopg2.connect(**DSL, cursor_factory=DictCursor) as pg_conn, pg_conn.cursor() as pg_cur:
                while True:
                    offset = state.get_state(key='offset_second')
                    sql_query = sql.SQL('''SELECT fw.id, fw.modified FROM content.film_work fw
                                            INNER JOIN {table} m2m ON m2m.filmwork_id = fw.id
                                            WHERE m2m.{column} IN ({}) AND fw.modified > {check_time} 
                                            ORDER BY fw.modified 
                                            LIMIT {limit} OFFSET {offset}''').format(sql.SQL(', ').join(map(sql.Literal, list_id)),
                                                                                     table=sql.Identifier(
                        'content', table),
                        column=sql.Identifier(
                        column),
                        check_time=sql.Literal(
                        check_time),
                        offset=sql.Literal(
                        offset),
                        limit=sql.Literal(limit))
                    pg_cur.execute(sql_query)
                    raw = [uuid[0] for uuid in pg_cur.fetchall() if uuid]
                    result += raw
                    if not raw:
                        state.set_state('offset_second', 0)
                        break

                    result += raw
                    state.set_state('offset_second', offset+limit)

                logger.info('coro_2 is ended')
                next_coroutine.send(result)
    except GeneratorExit:

        next_coroutine.close()


@init_generator
@backoff()
def data_upload_third_stage(next_coroutine: Coroutine, limit=100) -> Generator:
    """выгрузка данных, третий этап
    получает список id фильмов, в которых произошли изменения, возвращает список фильмов"""
    try:
        while True:
            list_id = (yield)
            result = []
            with psycopg2.connect(**DSL, cursor_factory=DictCursor) as pg_conn, pg_conn.cursor() as pg_cur:
                while True:
                    offset = state.get_state(key='offset_third')
                    sql_query = sql.SQL('''SELECT
                                            fw.id,
                                            fw.title, 
                                            fw.description, 
                                            fw.rating, 
                                            fw.type,
                                            array_agg(distinct p.id || ';' || p.first_name || ';' || pfw.role) as person,
                                            array_agg(distinct g.name) as genres
                                        FROM content.film_work fw
                                        LEFT JOIN content.person_film_work pfw ON pfw.filmwork_id = fw.id
                                        LEFT JOIN content.person p ON p.id = pfw.person_id
                                        LEFT JOIN content.genre_film_work gfw ON gfw.filmwork_id = fw.id
                                        LEFT JOIN content.genre g ON g.id = gfw.genre_id
                                        WHERE fw.id IN ({})
                                        GROUP BY fw.id
                                        LIMIT {limit} OFFSET {offset}''').format(sql.SQL(', ').join(map(sql.Literal, list_id)),
                                                                                 offset=sql.Literal(
                        offset),
                        limit=sql.Literal(limit))
                    pg_cur.execute(sql_query)
                    raw = pg_cur.fetchall()

                    if not raw:
                        state.set_state('offset_third', 0)
                        break
                    result += raw
                    state.set_state('offset_third', offset+limit)

                logger.info('coro_3 is ended')
                next_coroutine.send(result)
    except GeneratorExit:
        next_coroutine.close()
