#!/bin/bash

source .env

docker exec -i postgres pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_HOST_PATH"/db_backup_"$(date +%F_%H-%M-%S)".sql
find "$BACKUP_HOST_PATH"/* -mtime +1 -exec rm {} \;