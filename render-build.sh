#!/usr/bin/env bash
# render-build.sh — runs during Render's build phase

set -o errexit   # exit on error

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
