# syntax=docker/dockerfile:1.2

FROM python:3.8-alpine

WORKDIR /app

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt && \
python setup.py install
