.PHONY: build start run

build:
	docker build -t onyx-console .

start:
	docker run -p 5000:5000 -d -v onyx-storage:/storage onyx-console

run:
	docker run -p 5000:5000 -v onyx-storage:/storage onyx-console

default: build start