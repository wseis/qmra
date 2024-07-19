#! /bin/bash

set -e

source ./django_deployment_vars


# The production settings
mkdir -p /etc/opt/$DJANGO_PROJECT
cat <<-EOF1 >/etc/opt/$DJANGO_PROJECT/settings.py
	from $DJANGO_PROJECT.settings import *

	DEBUG = False
	ALLOWED_HOSTS = ['$DOMAIN', 'www.$DOMAIN']
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3',
	        'NAME': '/var/opt/$DJANGO_PROJECT/$DJANGO_PROJECT.db',
	    }
	}

	SERVER_EMAIL = 'noreply@$DOMAIN'
	DEFAULT_FROM_EMAIL = 'noreply@$DOMAIN'
	ADMINS = [
	    ('$ADMIN_NAME', '$ADMIN_EMAIL_ADDRESS'),
	]
	MANAGERS = ADMINS

	LOGGING = {
	    'version': 1,
	    'disable_existing_loggers': False,
	    'formatters': {
	        'default': {
	            'format': '[%(asctime)s] %(levelname)s: '
	                      '%(message)s',
	        }
	    },
	    'handlers': {
	        'file': {
	            'class': 'logging.handlers.'
	                     'TimedRotatingFileHandler',
	            'filename': '/var/log/$DJANGO_PROJECT/'
	                        '$DJANGO_PROJECT.log',
	            'when': 'midnight',
	            'backupCount': 60,
	            'formatter': 'default',
	        },
	    },
	    'root': {
	        'handlers': ['file'],
	        'level': 'INFO',
	    },
	}

	CACHES = {
	    'default': {
	        'BACKEND': 'django.core.cache.backends.filebased.'
	                   'FileBasedCache',
	        'LOCATION': '/var/cache/$DJANGO_PROJECT/cache',
	    }
	}
	STATIC_ROOT = '/var/cache/$DJANGO_PROJECT/static/'
	STATIC_URL = '/static/'

EOF1

chgrp $DJANGO_GROUP /etc/opt/$DJANGO_PROJECT

chmod u=rwx,g=rx,o= /etc/opt/$DJANGO_PROJECT

/var/opt/$DJANGO_PROJECT/miniconda3/envs/$DJANGO_PROJECT/bin/python -m compileall \
	/etc/opt/$DJANGO_PROJECT

mkdir -p /var/cache/$DJANGO_PROJECT/cache
chown $DJANGO_USER /var/cache/$DJANGO_PROJECT/cache
