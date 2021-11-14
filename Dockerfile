# syntax=docker/dockerfile:1.2

FROM python:3.8-alpine

WORKDIR /app

COPY . .

RUN apk add --no-cache python3-dev \
                       gcc \
                       libffi-dev \
                       libc-dev \
                       && rm -rf /var/cache/apk/

RUN python setup.py install
