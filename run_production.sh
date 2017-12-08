#!/usr/bin/env bash

# wait for PSQL server to start
sleep 10


# prepare init migration
python manage.py makemigrations
# migrate db, so we have the latest db schema
python manage.py migrate
# start development server on public ip interface, on port 8000
python manage.py collectstatic -c --noinput

uwsgi --ini /srv/tickist/backend/uwsgi.ini