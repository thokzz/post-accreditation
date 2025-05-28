# Makefile (Development Helper)
.PHONY: help build run stop clean logs shell db-init db-reset

help:
	@echo "Available commands:"
	@echo "  build     - Build Docker images"
	@echo "  run       - Start the application"
	@echo "  stop      - Stop the application"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  logs      - View application logs"
	@echo "  shell     - Access application shell"
	@echo "  db-init   - Initialize database"
	@echo "  db-reset  - Reset database"

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

logs:
	docker-compose logs -f web

shell:
	docker-compose exec web bash

db-init:
	docker-compose exec web flask init-db

db-reset:
	docker-compose exec web flask reset-db

create-admin:
	docker-compose exec web flask create-admin
