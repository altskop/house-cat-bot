FROM python:3.6-alpine

WORKDIR /OnyxBot

ADD . /OnyxBot

RUN apk --update add --no-cache git gcc build-base linux-headers ca-certificates python3-dev libffi-dev libressl-dev libxslt-dev \
    && pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice] \
    && rm -rf /var/lib/apt/lists/*

CMD [ "python", "-u", "./onyx.py" ]