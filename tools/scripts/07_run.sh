set -e

source ./django_deployment_vars

apt install gunicorn -y


su - $DJANGO_USER -c "source /var/opt/$DJANGO_PROJECT/miniconda3/bin/activate && conda activate $DJANGO_PROJECT && \
                    cd /opt/$DJANGO_APP_LOCATION && export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_APP_LOCATION && \
                    export DJANGO_SETTINGS_MODULE=settings && cd /opt/$DJANGO_APP_LOCATION && \
                    python manage.py collectstatic --noinput && gunicorn $DJANGO_APP_DIR.wsgi:application --daemon"
