.PHONY: up down rebuild frontend logs run-debug run-prod help

help:
	@echo "Команды:"
	@echo "  make run-debug   Запуск в режиме теста (без входа через MAX): DEBUG=True, ENABLE_DEMO_LOGIN=True, VITE_MOCK_AUTH=true (демо-логин)."
	@echo "  make run-prod    Запуск 'прод'-режима для проверки: DEBUG=False, ENABLE_DEMO_LOGIN=False, VITE_MOCK_AUTH=false (вход через MAX по ?token=...)."
	@echo "  make up          docker compose up -d (использует текущий .env)"
	@echo "  make down        docker compose down"
	@echo "  make rebuild     Полная пересборка без кэша"
	@echo "  make frontend    Пересборка только nginx-фронтенда"
	@echo "  make logs        Логи контейнеров (tail -100)"

run-debug:
	@test -f .env || (echo "Нет .env. Скопируйте .env.example: cp .env.example .env и заполните SECRET_KEY, ENCRYPTION_PEPPER, GIGACHAT_CREDENTIALS и т.д."; exit 1)
	DEBUG=True ENABLE_DEMO_LOGIN=True VITE_MOCK_AUTH=true \
		docker compose up --build -d

run-prod:
	@test -f .env || (echo "Нет .env. Скопируйте .env.example: cp .env.example .env и заполните SECRET_KEY, ENCRYPTION_PEPPER, GIGACHAT_CREDENTIALS и т.д."; exit 1)
	DEBUG=False ENABLE_DEMO_LOGIN=False VITE_MOCK_AUTH=false \
		docker compose up --build -d

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