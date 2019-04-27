FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8

ENV STATIC_PATH /app/aitaws/static

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app
