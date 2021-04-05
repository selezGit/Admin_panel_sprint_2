# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add tzdata

# install dependencies
RUN pip install --upgrade pip
COPY requirements /tmp/
RUN pip install -r /tmp/dev.txt

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app -g 1000 && adduser -u 1000 -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]