set -e

source ./infra/deployment_scripts/django_deployment_vars

git pull

source venv/bin/activate &&
python3 manage.py migrate &&
python3 manage.py collectstatic --no-input --clear &&

docker compose down 
docker compose up -d --build