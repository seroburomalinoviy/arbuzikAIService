#!/bin/bash
git pull origin main
rm -R ~/postgresql/data
docker compose stop
docker compose down
docker compose up -d
docker compose exec -it django sh -c 'chmod +x create_admin.sh && ./create_admin.sh'
echo "Reload finished!"