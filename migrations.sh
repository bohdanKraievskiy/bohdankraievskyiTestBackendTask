#!/bin/bash

docker-compose exec backend-app sh -c "cd /app/database alembic revision --autogenerate"
