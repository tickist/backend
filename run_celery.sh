#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
celery -A tickist worker -l info

