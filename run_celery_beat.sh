#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

celery -A tickist beat --loglevel=INFO --pidfile=/tmp/celerybeat-myapp.pid -S djcelery.schedulers.DatabaseScheduler

