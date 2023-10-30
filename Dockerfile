FROM python:3.10-slim

ENV TZ="America/Los_Angeles"

RUN apt-get update && apt-get install -y --no-install-recommends \
  libsqlite3-mod-spatialite && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

ENV SPATIALITE_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/mod_spatialite.so

WORKDIR /app

COPY requirements.txt /app

# RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install -r requirements.txt

COPY . /app
