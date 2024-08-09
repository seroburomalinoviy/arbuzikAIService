#!/bin/sh

docker compose exec postgres
pg_dump -h db -U "$POSTGRES_USER" "$POSTGRES_DB" > /backups/db_backup_"$(date +%F_%H-%M-%S)".sql