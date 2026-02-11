.PHONY: up down build logs restart backend-logs bot-logs

# Запустить все сервисы
up:
	docker compose up -d --build

# Остановить все
down:
	docker compose down

# Пересобрать и запустить
build:
	docker compose build --no-cache
	docker compose up -d

# Логи всех сервисов
logs:
	docker compose logs -f

# Логи backend
backend-logs:
	docker compose logs -f backend

# Логи бота
bot-logs:
	docker compose logs -f bot

# Логи celery
celery-logs:
	docker compose logs -f celery

# Перезапустить backend
restart-backend:
	docker compose restart backend

# Перезапустить бота
restart-bot:
	docker compose restart bot

# Зайти в контейнер backend
shell-backend:
	docker compose exec backend bash

# Зайти в PostgreSQL
shell-db:
	docker compose exec postgres psql -U water_user -d water_db

# Зайти в Redis
shell-redis:
	docker compose exec redis redis-cli

# Запустить миграции
migrate:
	docker compose exec backend alembic upgrade head

# Запустить тесты backend
test:
	docker compose exec backend pytest tests/ -v

# Статус сервисов
status:
	docker compose ps

# Очистить всё (включая volumes)
clean:
	docker compose down -v --remove-orphans
