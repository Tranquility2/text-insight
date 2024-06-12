#!/usr/bin/env bash

export LANG=C.UTF-8
export LANG=C.UTF-8

export PYTHONPATH="${PYTHONPATH}:./code"

# Start Redis
/usr/bin/redis-server --daemonize yes
# Start Celery
celery -A tasks worker -l info -P prefork &
# Start Gunicorn
gunicorn --workers 4 server:app -b 0.0.0.0:80