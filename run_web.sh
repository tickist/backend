#!/bin/sh

# wait for PSQL server to start
sleep 10


# prepare init migration
python manage.py makemigrations
# migrate db, so we have the latest db schema
python manage.py migrate
# start development server on public ip interface, on port 8000
python manage.py collectstatic -c -l --noinput

python manage.py runserver 0.0.0.0:8000