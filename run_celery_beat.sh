#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

celery -A tickist beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
