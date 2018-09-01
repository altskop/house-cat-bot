FROM python:3.6-alpine as base

RUN apk --update add --no-cache \
    git \
    gcc \
    build-base \
    linux-headers \
    ca-certificates \
    python3-dev \
    libffi-dev \
    libressl-dev \
    libxslt-dev

RUN pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice] gtts

FROM python:3.6-alpine

COPY --from=base /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

WORKDIR /OnyxBot

ADD . /OnyxBot

RUN apk --update add --no-cache \
    opus \
    ffmpeg \
    bash \
    sqlite

CMD [ "python", "-u", "./onyx.py" ]