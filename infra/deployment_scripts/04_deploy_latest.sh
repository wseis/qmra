set -e

source ./infra/deployment_scripts/django_deployment_vars

git pull

docker compose down 
DOMAIN_NAME=dev.qmra.org docker compose up -d --build --force-recreate