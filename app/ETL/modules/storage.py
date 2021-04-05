import abc
import json
import time
from typing import Any

import redis

from . import logger


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: redis.Redis):
        self.redis_adapter = redis_adapter

    def save_state(self, state: dict) -> None:
        while True:
            try:
                self.redis_adapter.set('data', json.dumps(state))
                return
            except redis.exceptions.ConnectionError:
                time.sleep(2)
                logger.info('trying connect to redis')

    def retrieve_state(self) -> dict:
        while True:
            try:
                raw_data = self.redis_adapter.get('data')
                if raw_data is None:
                    return {}
                return json.loads(raw_data)
            except redis.exceptions.ConnectionError:
                time.sleep(2)
                logger.info('trying connect to redis')


class State:
    """
     Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = self.retrieve_state()

    def retrieve_state(self) -> dict:

        data = self.storage.retrieve_state()

        if not data:
            return {}
        return data

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.state[key] = value

        self.storage.save_state(self.state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.state.get(key)
