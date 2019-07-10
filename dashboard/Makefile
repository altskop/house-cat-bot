.PHONY: build start run

build:
	docker build -t house-cat-dashboard .

start:
	docker run -p 5000:5000 -d -v house-cat-storage:/storage --restart unless-stopped house-cat-dashboard

run:
	docker run -p 5000:5000 -v house-cat-storage:/storage house-cat-dashboard

default: build start