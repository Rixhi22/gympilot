#!/bin/bash

# go to project
cd /Users/rishibala/ProjectR

# activate virtualenv
source venv/bin/activate

# folder where backups stored
BACKUP_DIR="/Users/rishibala/ProjectR/backups"

# delete backups older than 7 days
find "$BACKUP_DIR" -name "*.xlsx" -type f -mtime +7 -delete

# create new backup
python manage.py backup_excel
