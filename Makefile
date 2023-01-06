NODE_ENV?=production
env ?= .env.${NODE_ENV}
include $(env)
export $(shell sed 's/=.*//' $(env))

.PHONY: up
up:
	docker-compose --env-file .env.${NODE_ENV} --profile ${NODE_ENV}  up -d --remove-orphans && make logs 

.PHONY: down
down:
	docker-compose down -v

.PHONY: update
update:
	docker-compose pull

.PHONY: build
build:
	docker-compose build

.PHONY: logs
logs:
	docker-compose logs -f backend

.PHONY: restart
restart:
	docker-compose restart

.PHONY: restart-force
restart-force:
	docker-compose down -v && docker-compose --env-file .env.${NODE_ENV} --profile ${NODE_ENV} up -d --remove-orphans && make logs 

.PHONY: test
test:
	echo ${DB_PASS}