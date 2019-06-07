.PHONY: build start run

build:
	docker build -t onyx-bot .

start:
	docker run -d -v onyx-storage:/storage onyx-bot

run:
	docker run -v onyx-storage:/storage onyx-bot

default: build start