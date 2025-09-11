#!/usr/bin/env bash
# build.sh

set -o errexit

pip install -r requirements.txt
pip install -r requirements_remote.txt
mkdir -p media/profile_pics
mkdir -p accounts/static/
python manage.py collectstatic --noinput
python manage.py migrate_media
python manage.py migrate_media_to_cloudinary
python manage.py cleanup_media
python manage.py cleanup_broken_media
python manage.py upload_default_avatar
python manage.py debug_profile_pictures
python manage.py test_cloudinary
python manage.py test_cloudinary_upload
python manage.py debug_cloudinary_storage
python manage.py test_storage_urls
python manage.py test_url_utility
python manage.py test_cloudinary_direct
python manage.py cleanup_cloudinary

python manage.py migrate

