#!/bin/sh
cp -r /usr/local/lib/python3.8/site-packages/django/contrib/admin/static/ /home/app/web/staticfiles/;

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py makemigrations movie_admin
python manage.py migrate


exec "$@"