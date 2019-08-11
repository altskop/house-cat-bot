FROM tiangolo/meinheld-gunicorn-flask:python3.7

COPY ./app /app

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN apt-get update

RUN apt-get install -y ffmpeg \
    postgresql-9.6