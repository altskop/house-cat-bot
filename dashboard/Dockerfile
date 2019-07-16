FROM python:3.6-alpine as base

RUN apk --update add --no-cache \
    git \
    gcc \
    g++ \
    build-base \
    linux-headers \
    ca-certificates \
    python3-dev \
    libffi-dev \
    libressl-dev \
    libxslt-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

FROM python:3.6-alpine

COPY --from=base /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

RUN mkdir /web_console

ADD . /web_console

WORKDIR /web_console

RUN apk --update add --no-cache \
    ffmpeg \
    bash

EXPOSE 5000

CMD [ "python", "-u", "./app.py" ]