#!/bin/bash
docker compose down
git pull origin main
rm -R ~/postgresql/data
docker compose up -d
echo "Reload finished!"