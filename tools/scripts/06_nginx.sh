#! /bin/bash

apt install nginx -y


set -e

source ./django_deployment_vars


cd /etc/nginx/sites-enabled
	[ -e $DOMAIN ] \
		|| ln -s ../sites-available/$DOMAIN .

mkdir -p /var/www/$DOMAIN

## collect static

mkdir -p /var/cache/$DJANGO_PROJECT/static

chown $DJANGO_USER /var/cache/$DJANGO_PROJECT/static 


mkdir -p /var/cache/$DJANGO_PROJECT/cache

chown $DJANGO_USER /var/cache/$DJANGO_PROJECT/cache 




# Configuring nginx for django
	# Setting up nginx
cat <<-EOF1 >/etc/nginx/sites-available/$DOMAIN
    server {
        listen 80;
        listen [::]:80;
        server_name $DOMAIN www.$DOMAIN;
        root /var/www/$DOMAIN;
        location / {
            proxy_pass http://localhost:8000;
            proxy_set_header Host \$http_host;
            proxy_redirect off;
            proxy_set_header X-Forwarded-For \$remote_addr;
            proxy_set_header X-Forwarded-Proto \$scheme;
            client_max_body_size 20m;
        }
        location /static/ {
            alias /var/cache/$DJANGO_PROJECT/static/;
        }
    }
EOF1

#source /var/opt/$DJANGO_PROJECT/miniconda3/bin/activate
#conda activate $DJANGO_PROJECT

#cd /opt/$DJANGO_PROJECT
#PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT 

su - $DJANGO_USER -c "source /var/opt/$DJANGO_PROJECT/miniconda3/bin/activate && conda activate $DJANGO_PROJECT && \
                    cd /opt/$DJANGO_PROJECT && export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT && \
                    export DJANGO_SETTINGS_MODULE=settings && \
                    python manage.py collectstatic"


#python manage.py collectstatic
#/var/opt/$DJANGO_PROJECT/miniconda3/envs/$DJANGO_PROJECT/bin/python \
#/opt/$DJANGO_PROJECT/manage.py collectstatic \
#--settings=settings --noinput
service nginx stop
service nginx start

