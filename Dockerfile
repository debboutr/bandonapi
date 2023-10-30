FROM python:3.10-slim

ENV TZ="America/Los_Angeles"

RUN apt-get update && apt-get install -y --no-install-recommends \
  libsqlite3-mod-spatialite && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# CMD ["python", "-m", "http.server"]
