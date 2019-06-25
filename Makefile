.PHONY: storage

storage:
	docker volume rm onyx-storage
	docker container create --name dummy -v onyx-storage:/storage hello-world
	docker volume create --name onyx-storage
	docker cp storage/. dummy:/storage
	docker rm dummy