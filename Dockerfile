# pull official base image
FROM python:3.12.5-slim

# set work directory
WORKDIR qmra

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update && apt upgrade -y
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

# copy project
COPY ./qmra ./qmra
COPY ./manage.py .