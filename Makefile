.PHONY: build run

build:
	docker build -t onyx-bot .

run:
	docker run -d --name=onyx-bot onyx-bot

default: build run