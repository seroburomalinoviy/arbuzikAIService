#!/bin/bash
docker compose down
git pull origin main
rm -R ~/postgresql/data
rm django_bot/bot/migrations/* -r
docker compose up -d
echo "Reload finished!"