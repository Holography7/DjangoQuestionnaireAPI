#!/bin/sh
python manage.py migrate --noinput
python manage.py loaddata questiontype.json
python manage.py loaddata groups.json
python manage.py collectstatic --no-input --clear
exec "$@"
