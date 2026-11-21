
.PHONY: up down rebuild frontend logs

up:
	docker compose up -d

down:
	docker compose down

rebuild:
	docker compose build --no-cache
	docker compose up -d --force-recreate

frontend:
	docker compose build --no-cache nginx
	docker compose up -d --force-recreate nginx

logs:
	docker compose logs -f --tail=100
