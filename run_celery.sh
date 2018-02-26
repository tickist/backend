#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

celery -A tickist worker -l info
