#! /bin/bash

set -e

source ./django_deployment_vars

# The programm files
cd /opt
[ -d $DJANGO_PROJECT/.git ] || git clone $DJANGO_PROJECT_REPOSITORY

mv ./$REPOSITORY_NAME ./$DJANGO_PROJECT

su - $DJANGO_USER -c "/var/opt/$DJANGO_PROJECT/miniconda3/envs/$DJANGO_PROJECT/bin/pip install -r /opt/$DJANGO_PROJECT/requirements.txt"

/var/opt/$DJANGO_PROJECT/miniconda3/envs/$DJANGO_PROJECT/bin/python -m compileall /opt/$DJANGO_PROJECT


# The log directory
mkdir -p /var/log/$DJANGO_PROJECT
chown $DJANGO_USER /var/log/$DJANGO_PROJECT

# install gdal
apt-get install gdal-bin -y

su - $DJANGO_USER -c "source /var/opt/$DJANGO_PROJECT/miniconda3/bin/activate && conda activate $DJANGO_PROJECT && \
                    cd /opt/$DJANGO_PROJECT && export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT && \
                    export DJANGO_SETTINGS_MODULE=settings && \
                    python manage.py migrate"

