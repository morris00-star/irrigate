#!/usr/bin/env bash
# build.sh

set -o errexit

pip install -r requirements.txt
pip install -r requirements_remote.txt
python manage.py collectstatic --noinput
python manage.py migrate
