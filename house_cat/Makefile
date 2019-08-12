.PHONY: build start run

build:
	docker build -t house-cat-bot .

start:
	docker run -d -v house-cat-storage:/storage --env-file config.env --log-opt max-size=10m --log-opt max-file=5 --restart unless-stopped --name house-cat-bot house-cat-bot

run:
	docker run -v house-cat-storage:/storage --env-file config.env --log-opt max-size=10m --log-opt max-file=5 --name house-cat-bot house-cat-bot

stop:
	docker stop house-cat-bot

default: build start