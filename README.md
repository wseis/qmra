# qmra
Web-application for calculating microbial risk for drinking water and water reuse systems.

# Installation
This software can be found [here]("https://www.qmra.org"), but also can be run locally. 
For local installation:

    - install git
    - setup and activate a virtual environment
    - clone this repository
    - cd into qmra/tools

### Install django

```bash
pip install django

```
### Install necessary requirements

```bash
pip install -r requirements.txt

```
### Create new superuser for admin page

```bash
python manage.py createsuperuser
```

### run app locally

```bash
python manage.py runserver
```


