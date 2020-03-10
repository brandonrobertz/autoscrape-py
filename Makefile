start:
	docker-compose down
	#docker-compose build --pull
	docker-compose up --build -t0 --abort-on-container-exit --renew-anon-volumes

quickstart:
	docker-compose up -t0 --abort-on-container-exit

build:
	docker-compose build --pull

stop:
	docker-compose down -t0
	docker-compose rm -f -v # -v removes _anonymous_ volumes

clean: stop
	if docker ps -a -q; then \
		docker rm -f $$(docker ps -a -q) || exit 0; \
	fi
	if docker images -q; then \
		docker rmi -f $$(docker images -q) || exit 0; \
	fi
	docker volume rm -f $$(docker volume ls | awk '{ print $$2 }')

run_rabbitmq:
	docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

update_www:
	git submodule init && git submodule update && cd www && git fetch && git reset origin/master --hard

commit_www:
	git add www && git commit -m "Update www"
