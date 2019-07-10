.PHONY: storage

storage:
	docker volume rm house-cat-storage
	docker container create --name dummy -v house-cat-storage:/storage hello-world
	docker volume create --name house-cat-storage
	docker cp storage/. dummy:/storage
	docker rm dummy