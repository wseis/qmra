#! /bin/bash

set -e

source ./infra/deployment_scripts/django_deployment_vars

DJANGO_USER=$DJANGO_PROJECT
DJANGO_GROUP=$DJANGO_PROJECT

# Creating a user and group
if ! getent passwd $DJANGO_PROJECT; then
	adduser --system --home=/var/opt/$DJANGO_PROJECT \
		--no-create-home --disabled-password --group \
		--shell=/bin/bash $DJANGO_USER
fi

# install deps

source venv/bin/activate
pip install -r requirements.txt

# create initial db


python3 manage.py migrate
python3 manage.py seed_qmra

## collect static

mkdir -p /var/cache/qmra/static
chown $DJANGO_USER /var/cache/qmra/static

python manage.py collectstatic --clear --no-input

service nginx stop
service nginx start

