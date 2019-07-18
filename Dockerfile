FROM python:3-alpine3.9
LABEL Name=moviesdb Version=0.1 Maintainer="kamil.kiljan@outlook.com"

# EXPOSE 8000
WORKDIR /moviesdb
ADD . /moviesdb
RUN python3 -m pip install -r requirements.txt
RUN python moviesdb/manage.py makemigrations api
RUN python moviesdb/manage.py migrate
CMD python moviesdb/manage.py runserver 0.0.0.0:8000
