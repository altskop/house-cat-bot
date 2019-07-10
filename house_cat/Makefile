.PHONY: build start run

build:
	docker build -t house-cat-bot .

start:
	docker run -d -v house-cat-storage:/storage --env-file config.env --restart unless-stopped house-cat-bot

run:
	docker run -v house-cat-storage:/storage --env-file config.env house-cat-bot

default: build start