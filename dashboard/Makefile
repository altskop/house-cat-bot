.PHONY: build start run

build:
	docker build -t house-cat-dashboard .

start:
	docker run -p 5000:5000 -d -v house-cat-storage:/storage --env-file config.env --log-opt max-size=10m --log-opt max-file=5 --restart unless-stopped house-cat-dashboard

run:
	docker run -p 5000:5000 -v house-cat-storage:/storage --env-file config.env --log-opt max-size=10m --log-opt max-file=5 house-cat-dashboard

default: build start