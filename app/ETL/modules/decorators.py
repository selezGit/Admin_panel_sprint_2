import logging
import time
from functools import wraps
from typing import Any, Callable, Coroutine

import elasticsearch
import psycopg2
import redis
import requests

from . import logger


def init_generator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Coroutine:
        g = func(*args, **kwargs)
        next(g)
        return g
    return wrapper


def backoff():
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. 
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)


    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """
    start_sleep_time = 0.1
    factor = 2
    border_sleep_time = 10

    def waiter(tries: int) -> None:
        wait = start_sleep_time * (factor**tries)
        if wait >= border_sleep_time:
            wait = border_sleep_time
        logging.info('Backing off %.1f seconds afters %d tries', wait, tries)
        time.sleep(wait)

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            tries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except psycopg2.OperationalError:
                    logger.error('trying connect to db')
                    waiter(tries)
                    tries += 1
                except redis.exceptions.ConnectionError:
                    logger.error('trying connect to redis')
                    waiter(tries)
                    tries += 1
                except requests.exceptions.ConnectionError:
                    logger.error('trying create schema of elastic')
                    waiter(tries)
                    tries += 1
                except elasticsearch.exceptions.ConnectionError:
                    logger.error('trying reconnect to elastic')
                    waiter(tries)
                    tries += 1

        return inner
    return func_wrapper
