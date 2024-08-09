#!/bin/bash

#while true;
#do sleep 24h;
pg_dump -h db -U $DB_USER $DB_NAME > /backups/db_backup_$(date +%F_%H-%M-%S).sql;
#done;