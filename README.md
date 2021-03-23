# Admin panel sprint 2

## Описание сервиса

Панель администратора для сайта с фильмами, по умолчанию находится по адресу http://localhost:80


## Используемые технологии

* Приложение запускается под управлением сервера **WSGI/ASGI**.
* Для отдачи [статических файлов](https://nginx.org/ru/docs/beginners_guide.html#static) используется **Nginx.**
* Виртуализация осуществляется в **Docker.**

## Основные компоненты системы

1. **Cервер WSGI/ASGI** — сервер с запущенным приложением.
2. **Nginx** — прокси-сервер, который является точкой входа для web-приложения.
3. **PostgreSQL** — реляционное хранилище данных. 
<!-- 4. **ETL** — механизм обновления данных между PostgreSQL и ES. -->

### Схема сервиса

![all](images/all.png)

## Настройки

В корне проекта необходимо создать файл `.env` со следующим содержанием:

######[ Django ] ######
DEBUG=1
SECRET_KEY = 'example'
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

######[ Postgresql ] ######
POSTGRES_USER = django_admin 
POSTGRES_DB = movie_admin
POSTGRES_PASSWORD = 1234

######[ Django DB ] ######
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=movie_admin
SQL_USER=django_admin
SQL_PASSWORD=1234
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres

## Запуск контейнера:
В корне проекта выполняем команду:

    $ docker-compose up -d --build

### Наполнение контентом
Что бы перенести фильмы из **SQLite** в **Postgres** необходимо запустить скрипт из папки `sqlite_to_postgres`:

Убедитесь, что у вас установлен [psycopg2](https://pypi.org/project/psycopg2/):

    $ pip install psycopg2-binary

При запущенном сервере, запускаем команду загрузки фильмов.

    $ python sqlite_to_postgres/load_data.py