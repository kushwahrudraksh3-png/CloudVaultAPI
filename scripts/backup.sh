#!/bin/bash

set -Eeuo pipefail

source .env

export PGPASSWORD="$DB_PASSWORD"

BACKUP_DIR="backups"

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/cloudvault_$TIMESTAMP.sql"

pg_dump \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  > "$BACKUP_FILE"

unset PGPASSWORD
