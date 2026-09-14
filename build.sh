#!/bin/bash
set -o errexit

pip install -r requirements.txt --break-system-packages
python manage.py collectstatic --noinput
python manage.py migrate
