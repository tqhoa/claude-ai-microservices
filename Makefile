.PHONY: dev prod down down-clean logs logs-engine logs-gateway migrate migration test-engine test-frontend shell-engine shell-db ps health

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

down:
	docker compose down

down-clean:
	docker compose down -v --rmi local

logs:
	docker compose logs -f $(service)

logs-engine:
	docker compose logs -f engine

logs-gateway:
	docker compose logs -f gateway

migrate:
	docker compose exec engine alembic upgrade head

migration:
	docker compose exec engine alembic revision --autogenerate -m "$(msg)"

test-engine:
	docker compose exec engine pytest --cov=app

test-frontend:
	docker compose exec frontend pnpm test

shell-engine:
	docker compose exec engine bash

shell-db:
	docker compose exec db psql -U postgres -d appdb

ps:
	docker compose ps

health:
	curl -sf http://localhost/health && curl -sf http://localhost/api/health
