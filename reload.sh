#!/bin/bash
git pull origin main
rm -R ~/postgresql/data
docker compose stop
docker compose down
docker compose up -d
echo "Reload finished!"