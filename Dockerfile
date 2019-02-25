FROM python:3.5

RUN apt-get update
RUN apt-get install -y vim postgresql-client
# add requirements.txt to the image
ADD requirements.txt /srv/tickist/backend/requirements.txt


WORKDIR /srv/tickist/backend/

# install python dependencies
RUN pip install -r requirements.txt
