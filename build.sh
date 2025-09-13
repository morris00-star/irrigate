#!/usr/bin/env bash
# build.sh

set -o errexit

pip install -r requirements.txt
pip install -r requirements_remote.txt
mkdir -p media/profile_pics
mkdir -p accounts/static/
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

