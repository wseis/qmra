set -e

source ./django_deployment_vars

apt install gunicorn -y

cp /opt/.env /opt/$DJANGO_PROJECT

su - $DJANGO_USER -c "source /var/opt/$DJANGO_PROJECT/miniconda3/bin/activate && conda activate $DJANGO_PROJECT && \
                    cd /opt/$DJANGO_PROJECT && export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT && \
                    export DJANGO_SETTINGS_MODULE=settings && cd /opt/$DJANGO_PROJECT && \
                    python manage.py collectstatic --noinput && gunicorn $DJANGO_PROJECT.wsgi:application --daemon"
