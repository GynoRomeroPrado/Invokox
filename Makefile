# ==============================================================================
# MAKEFILE - INVOKOX V2.0
# ==============================================================================
# Comandos útiles para desarrollo con Docker Compose
# ==============================================================================

.PHONY: help up down restart logs build clean test migrate shell

# Colores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Muestra esta ayuda
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(BLUE)  INVOKOX V2.0 - Docker Commands$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

up: ## Inicia todos los servicios en background
	@echo "$(BLUE)🚀 Iniciando servicios...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Servicios iniciados$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:5173$(NC)"
	@echo "$(YELLOW)Backend API: http://localhost:8000$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)Flower (Celery): http://localhost:5555$(NC)"

down: ## Detiene todos los servicios
	@echo "$(BLUE)🛑 Deteniendo servicios...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Servicios detenidos$(NC)"

restart: ## Reinicia todos los servicios
	@echo "$(BLUE)🔄 Reiniciando servicios...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Servicios reiniciados$(NC)"

logs: ## Muestra logs de todos los servicios
	docker-compose logs -f

logs-backend: ## Muestra logs del backend
	docker-compose logs -f backend

logs-frontend: ## Muestra logs del frontend
	docker-compose logs -f frontend

logs-celery: ## Muestra logs de Celery worker
	docker-compose logs -f celery-worker

build: ## Construye las imágenes de Docker
	@echo "$(BLUE)🔨 Construyendo imágenes...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Imágenes construidas$(NC)"

rebuild: ## Reconstruye las imágenes sin caché
	@echo "$(BLUE)🔨 Reconstruyendo imágenes sin caché...$(NC)"
	docker-compose build --no-cache
	@echo "$(GREEN)✓ Imágenes reconstruidas$(NC)"

clean: ## Detiene servicios y elimina volúmenes
	@echo "$(YELLOW)⚠️  Esta acción eliminará todos los datos$(NC)"
	@read -p "¿Estás seguro? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(RED)🗑️  Limpiando...$(NC)"; \
		docker-compose down -v; \
		echo "$(GREEN)✓ Limpieza completa$(NC)"; \
	fi

ps: ## Lista servicios en ejecución
	docker-compose ps

migrate: ## Ejecuta migraciones de Alembic
	@echo "$(BLUE)📦 Ejecutando migraciones...$(NC)"
	docker-compose exec backend alembic upgrade head
	@echo "$(GREEN)✓ Migraciones completadas$(NC)"

migrate-create: ## Crea nueva migración (uso: make migrate-create msg="descripcion")
	@if [ -z "$(msg)" ]; then \
		echo "$(RED)Error: Especifica un mensaje con msg=\"descripcion\"$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📝 Creando migración: $(msg)$(NC)"
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"
	@echo "$(GREEN)✓ Migración creada$(NC)"

migrate-down: ## Revierte última migración
	@echo "$(YELLOW)⚠️  Revirtiendo última migración...$(NC)"
	docker-compose exec backend alembic downgrade -1
	@echo "$(GREEN)✓ Migración revertida$(NC)"

shell-backend: ## Abre shell en contenedor backend
	docker-compose exec backend /bin/bash

shell-frontend: ## Abre shell en contenedor frontend
	docker-compose exec frontend /bin/sh

shell-db: ## Abre shell en PostgreSQL
	docker-compose exec postgres psql -U invokox_user -d invokox_db

shell-redis: ## Abre shell en Redis
	docker-compose exec redis redis-cli

test: ## Ejecuta tests del backend
	@echo "$(BLUE)🧪 Ejecutando tests...$(NC)"
	docker-compose exec backend pytest -v
	@echo "$(GREEN)✓ Tests completados$(NC)"

test-cov: ## Ejecuta tests con coverage
	@echo "$(BLUE)🧪 Ejecutando tests con coverage...$(NC)"
	docker-compose exec backend pytest --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage generado en htmlcov/$(NC)"

lint: ## Ejecuta linters (ruff + mypy)
	@echo "$(BLUE)🔍 Ejecutando linters...$(NC)"
	docker-compose exec backend ruff check src/
	docker-compose exec backend mypy src/
	@echo "$(GREEN)✓ Linting completado$(NC)"

format: ## Formatea código con black
	@echo "$(BLUE)✨ Formateando código...$(NC)"
	docker-compose exec backend black src/
	docker-compose exec backend ruff check --fix src/
	@echo "$(GREEN)✓ Código formateado$(NC)"

backup-db: ## Crea backup de la base de datos
	@echo "$(BLUE)💾 Creando backup...$(NC)"
	docker-compose exec -T postgres pg_dump -U invokox_user invokox_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup creado$(NC)"

restore-db: ## Restaura backup de la base de datos (uso: make restore-db file=backup.sql)
	@if [ -z "$(file)" ]; then \
		echo "$(RED)Error: Especifica archivo con file=backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)⚠️  Restaurando desde $(file)...$(NC)"
	docker-compose exec -T postgres psql -U invokox_user invokox_db < $(file)
	@echo "$(GREEN)✓ Backup restaurado$(NC)"

stats: ## Muestra estadísticas de uso de Docker
	docker stats --no-stream

prune: ## Limpia recursos no utilizados de Docker
	@echo "$(YELLOW)🧹 Limpiando recursos no utilizados...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✓ Limpieza completada$(NC)"

dev: up ## Alias para 'make up'

stop: down ## Alias para 'make down'
