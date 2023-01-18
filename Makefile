env ?=production
include .env.$(env)

ENV_SHORT = $(if $(findstring production,$(env)),prod,dev)

COMPOSE_STRING=docker-compose -f docker-compose.yml -f docker-compose.${ENV_SHORT}.yml --env-file .env.${env}

front:
	$(COMPOSE_STRING) --profile frontend up -d --remove-orphans
back:
	$(COMPOSE_STRING) --profile backend up -d --remove-orphans
db:
	$(COMPOSE_STRING) --profile mongo up -d --remove-orphans
up:
	$(COMPOSE_STRING) --profile default up -d --remove-orphans

down-front:
	$(COMPOSE_STRING) --profile frontend down -v
down-back:
	$(COMPOSE_STRING) --profile backend down -v
down-db:
	$(COMPOSE_STRING) --profile mongo down -v
down:
	$(COMPOSE_STRING) --profile default down -v

log-front:
	$(COMPOSE_STRING) logs -f frontend
log-back:
	$(COMPOSE_STRING) logs -f backend
log-db:
	$(COMPOSE_STRING) logs -f mongo
logs:
	$(COMPOSE_STRING) logs -f

restart-front:
	$(COMPOSE_STRING) restart frontend
restart-back:
	$(COMPOSE_STRING) restart backend
restart-db:
	$(COMPOSE_STRING) restart mongo
restart:
	$(COMPOSE_STRING) restart
