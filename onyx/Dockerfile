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

RUN pip install -U "discord.py[voice]" gtts pillow aenum

FROM python:3.6-alpine

COPY --from=base /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

RUN mkdir /onyxbot

ADD . /onyxbot

WORKDIR /onyxbot

RUN apk --update add --no-cache \
    opus \
    ffmpeg \
    bash \
    sqlite

CMD [ "python", "-u", "./onyx.py" ]