#!/bin/bash

# go to project
cd /Users/rishibala/GYM_PILOT

# activate virtualenv
source venv/bin/activate

# folder where backups stored
BACKUP_DIR="/Users/rishibala/GYM_PILOT/backups"

# current date
DATE=$(date +%Y-%m-%d)

# delete backups older than 7 days
find "$BACKUP_DIR" -name "*.xlsx" -type f -mtime +7 -delete
find "$BACKUP_DIR" -name "*.sql" -type f -mtime +7 -delete

# create Excel backup
python manage.py backup_excel

# create PostgreSQL backup
pg_dump "postgresql://postgres.irqmjuevdfyyciomfira:QB3tDr35HUk5NUre@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" > "$BACKUP_DIR/gympilot_$DATE.sql"

rclone copy "$BACKUP_DIR" gdrive:GymPilot_Backups

echo "Backup uploaded to Google Drive"

rclone delete --min-age 30d gdrive:GymPilot_Backups