#!/bin/sh

while true; do
  pg_dump -h db -U "$POSTGRES_USER" "$POSTGRES_DB" > /backups/db_backup_"$(date +%F_%H-%M-%S)".sql
  sleep 1m
done