#!/usr/bin/env bash

export PYTHONPATH="${PYTHONPATH}:./code"

gunicorn --workers 4 server:app -b 0.0.0.0:80