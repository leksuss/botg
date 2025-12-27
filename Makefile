.PHONY: lint lint-editorconfig lint-flake8 lint-all db-up db-down compose-up compose-down compose-logs help

help:
	@echo "Команды:"
	@echo "  make db-up           - Поднять dev Postgres (docker-compose.dev.yml)"
	@echo "  make db-down         - Остановить dev Postgres"
	@echo "  make lint            - Запустить все линтеры"
	@echo "  make lint-editorconfig - Проверить .editorconfig"
	@echo "  make lint-flake8     - Запустить flake8"
	@echo "  make compose-up      - Поднять продовый стек (docker-compose.yml)"
	@echo "  make compose-down    - Остановить продовый стек"
	@echo "  make compose-logs    - Логи продового стека"

lint: lint-editorconfig lint-flake8
	@echo "✅ Все линтеры прошли успешно!"

lint-all: lint

lint-editorconfig:
	@docker compose -f .linters/docker-compose.yml run -T --rm editorconfig-checker

lint-flake8:
	@docker compose -f .linters/docker-compose.yml run -T --rm linters

db-up:
	@docker compose -f docker-compose.dev.yml up -d

db-down:
	@docker compose -f docker-compose.dev.yml down

compose-up:
	@docker compose up -d --build --remove-orphans

compose-down:
	@docker compose down

compose-logs:
	@docker compose logs -f
