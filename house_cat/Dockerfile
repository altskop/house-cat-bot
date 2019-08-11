FROM python:3.6-alpine as base

RUN apk --update add --no-cache \
    git \
    gcc \
    g++ \
    build-base \
    linux-headers \
    ca-certificates \
    python3-dev \
    musl-dev \
    postgresql-dev \
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

RUN mkdir /house-cat-bot

ADD . /house-cat-bot

WORKDIR /house-cat-bot

RUN apk --update add --no-cache \
    opus \
    ffmpeg \
    bash \
    postgresql-dev \
    sqlite

CMD [ "python", "-u", "./house_cat.py" ]