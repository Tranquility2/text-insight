#!/usr/bin/env bash

export PYTHONPATH="${PYTHONPATH}:./code"

# Start Redis in the background
/usr/bin/redis-server --daemonize yes

gunicorn --workers 4 server:app -b 0.0.0.0:80