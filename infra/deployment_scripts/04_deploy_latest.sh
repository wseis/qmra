set -e

source ./infra/deployment_scripts/django_deployment_vars

git pull

docker compose down 
docker compose up -d --build --force-recreate