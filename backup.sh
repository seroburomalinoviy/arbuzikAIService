#!/bin/sh

docker exec -i container_name pg_dump --username pg_username [--password pg_password] db_name > /path/on/your/machine/dump.sql
pg_dump -h db -U "$POSTGRES_USER" "$POSTGRES_DB" > /backups/db_backup_"$(date +%F_%H-%M-%S)".sql