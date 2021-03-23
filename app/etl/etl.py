
import sqlite3
import uuid
import requests

from elasticsearch import Elasticsearch, helpers


class InsertFilms:
    def __init__(self):
        self.conn = sqlite3.connect('train.sqlite')
        self.cursor = self.conn.cursor()
        self.elastic = Elasticsearch(hosts=[{'host': '127.0.0.1', 'port': 9200}])
        self.movies = self.parse_sql_to_dict(self.get_sql_data())

        self.create_index()

        helpers.bulk(self.elastic, self.bulk_json_data(self.movies))
        print("data has been uploaded")
        self.conn.close()

    def create_index(self):
        '''функция создания и разметки индекса'''
        url = 'http://127.0.0.1:9200/movies'
        data = {
            "settings": {
                "refresh_interval": "1s",
                "analysis": {
                    "filter": {
                        "english_stop": {
                            "type":       "stop",
                            "stopwords":  "_english_"
                        },
                        "english_stemmer": {
                            "type": "stemmer",
                            "language": "english"
                        },
                        "english_possessive_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english"
                        },
                        "russian_stop": {
                            "type":       "stop",
                            "stopwords":  "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    },
                    "analyzer": {
                        "ru_en": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "english_stop",
                                "english_stemmer",
                                "english_possessive_stemmer",
                                "russian_stop",
                                "russian_stemmer"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "imdb_rating": {
                        "type": "float"
                    },
                    "genre": {
                        "type": "keyword"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "ru_en",
                        "fields": {
                            "raw": {
                                "type":  "keyword"
                            }
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "ru_en"
                    },
                    "director": {
                        "type": "text",
                        "analyzer": "ru_en"
                    },
                    "actors_names": {
                        "type": "text",
                        "analyzer": "ru_en"
                    },
                    "writers_names": {
                        "type": "text",
                        "analyzer": "ru_en"
                    },
                    "actors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                            },
                            "name": {
                                "type": "text",
                                "analyzer": "ru_en"
                            }
                        }
                    },
                    "writers": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                            },
                            "name": {
                                "type": "text",
                                "analyzer": "ru_en"
                            }
                        }
                    }
                }
            }
        }
        requests.put(url, json=data)
        print("index been created")

    def parse_sql_to_dict(self, data: dict) -> dict:
        '''
        функция получает на вход результат запроса к sql
        и приводит данные к нужному формату
        :data: данные загруженные из sql
        '''
        all_films = []
        for row in data:
            film = {}
            actors_ids, actors_names, plot, director, genre, movie_id, imdb_rating, title, writers_ids, writers_names = row

            if actors_ids is not None and actors_names is not None:
                actors = [
                    {'id': int(_id), 'name': name}
                    for _id, name in zip(actors_ids.split(','), actors_names.split(','))
                    if name != 'N/A'
                ]
                actors_names = [
                    x for x in actors_names.split(',') if x != 'N/A']

            if writers_ids is not None and writers_names is not None:
                writers = [
                    {'id': _id, 'name': name}
                    for _id, name in zip(writers_ids.split(','), writers_names.split(','))
                    if name != 'N/A'
                ]
                writers_names = [
                    x for x in writers_names.split(',') if x != 'N/A']

            film["id"] = movie_id
            film["title"] = title
            film["description"] = plot if plot != 'N/A' else None
            film["imdb_rating"] = None if imdb_rating == 'N/A' else float(
                imdb_rating)
            film["writers"] = writers
            film["actors"] = actors
            film["genre"] = genre.replace(' ', '').split(',')
            film["director"] = [x.strip() for x in director.split(',')
                                ] if director != 'N/A' else None
            film["actors_names"] = actors_names
            film["writers_names"] = writers_names


            all_films.append(film)
        return all_films

    def get_sql_data(self):
        '''функция получения данных из sqlite'''
        data = self.cursor.execute('''WITH json_writers as (SELECT movies.id, group_concat(DISTINCT value) as writers, group_concat(DISTINCT w.name) as name FROM movies, json_tree(writers)
                INNER JOIN writers w ON value=w.id
                WHERE NOT writers=''
                GROUP by movies.id),
                one_writer as (SELECT m.id, m.writer, w.name FROM movies m LEFT JOIN writers w ON m.writer=w.id WHERE NOT m.writer=''),
                all_writers as (select * from one_writer UNION select * from json_writers)

                SELECT distinct group_concat(distinct a.id), group_concat(distinct a.name), plot, director, genre, m.id, imdb_rating, title, aw.writer, aw.name from movies m 
                INNER JOIN movie_actors ma ON m.id = ma.movie_id 
                INNER JOIN actors a ON ma.actor_id = a.id 
                INNER JOIN all_writers aw ON m.id = aw.id
                GROUP BY m.id
                ''').fetchall()
        return data

    def bulk_json_data(self, data: dict):
        '''фукнция загрузки данных в ES
        :data: результат обработки данных из функции parse_sql_to_dict'''
        for doc in data:
            yield {
                "_index": "movies",
                "_id": uuid.uuid4(),
                "_source": doc
            }


if __name__ == '__main__':
    InsertFilms()
