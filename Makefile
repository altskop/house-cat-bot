.PHONY: build run

build:
	docker build -t onyx-bot .

run:
	docker volume create --name onyx-db
	docker run -d -v onyx-db:/OnyxBot/db onyx-bot

default: build run