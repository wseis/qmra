#! /bin/bash

apt install nginx -y


set -e

source ./infra/deployment_scripts/django_deployment_vars


# Configuring nginx for django
	# Setting up nginx
cat <<-EOF1 >/etc/nginx/sites-available/$DOMAIN
    server {
        listen 80;
        listen [::]:80;
        server_name $DOMAIN www.$DOMAIN;
        root /var/www/$DOMAIN;
        location / {
            proxy_pass http://localhost:8080;
            proxy_set_header Host \$http_host;
            proxy_redirect off;
            proxy_set_header X-Forwarded-For \$remote_addr;
            proxy_set_header X-Forwarded-Proto \$scheme;
            client_max_body_size 20m;
        }
        location /static/ {
            alias /var/cache/qmra/static/;
        }
    }
EOF1

cd /etc/nginx/sites-enabled
	[ -e $DOMAIN ] \
		|| ln -s ../sites-available/$DOMAIN .


service nginx start
apt install snapd -y
snap install core
snap refresh core
snap install --classic certbot
if [ ! -f /usr/bin/certbot ]; then
    ln -s /snap/bin/certbot /usr/bin/certbot
fi
certbot --nginx
