.PHONY: build run

build:
	docker build -t onyx-bot .

run:
	docker run -d onyx-bot

default: build run