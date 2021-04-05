import json
import time
from typing import Generator

import requests
from elasticsearch import Elasticsearch, helpers

from . import logger
from .decorators import backoff, init_generator


@backoff()
def create_index():
    """функция создания и разметки индекса"""
    url = 'http://elasticsearch:9200/'

    if requests.get(url + '_cat/indices/movies').status_code != 200:
        with open('ETL/modules/schema.json', 'r') as f:
            schema = json.load(f)
        requests.put(url + 'movies', json=schema)
        logger.info('Index "movies" been created')

def bulk_json_data(data: dict):
    """фукнция загрузки данных в ES
    :data: результат обработки данных"""
    for doc in data:
        yield {
            '_index': 'movies',
            '_id': doc.get('id'),
            '_source': doc
        }

@init_generator
@backoff()
def load_to_es() -> Generator:
    """Корутина загрузки данных в elasticsearch"""
    es = Elasticsearch()
    create_index()
    while True:
        bulk_data = yield
        while True:
            if es.ping():
                helpers.bulk(es, bulk_json_data(bulk_data))
                break
            else:
                logger.info('trying reconnect to elastic')
                time.sleep(2)
