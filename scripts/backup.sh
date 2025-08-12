#!/bin/bash

# === CONFIGURATION ===

# Backup base directory
BACKUP_DIR="/home/lr/backup/thinkpad_backup"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVE_DIR="$BACKUP_DIR/$TIMESTAMP"
ARCHIVE_FILE="$BACKUP_DIR/${TIMESTAMP}.tar.gz"
mkdir -p "$ARCHIVE_DIR"

# Docker container names
NEXTCLOUD_CONTAINER="nextcloud-nextcloud-1"
POSTGRES_CONTAINER="stick-it-db"
NEXTCLOUD_MYSQL="nextcloud-database-1"

# PostgreSQL config
PG_DBS=("stickitprod")
PG_USER="postgres"

# Folders outside Docker to back up
FOLDERS_TO_BACKUP=("/home/lr/bwdata" "/home/lr/server/MonaServer/minio/data/stick-it-prod")

# Remote backup target
REMOTE_USER="lr"
REMOTE_HOST="192.168.0.124"
REMOTE_PATH="/data/thinkpad_backup"
SSH_KEY="/home/lr/.ssh/key_medion"

mkdir -p $ARCHIVE_DIR/nextcloud/db
mkdir $ARCHIVE_DIR/postgres
mkdir $ARCHIVE_DIR/folders

echo "[INFO] Starting Docker-based backup at $TIMESTAMP"

# === NEXTCLOUD BACKUP ===
echo "[INFO] Backing up Nextcloud data..."
docker exec "$NEXTCLOUD_CONTAINER" /var/www/html/occ maintenance:mode --on

docker cp "$NEXTCLOUD_CONTAINER:/var/www/html" "$ARCHIVE_DIR/nextcloud/html"



docker exec -u root "$NEXTCLOUD_MYSQL" apt update
docker exec -u root "$NEXTCLOUD_MYSQL" apt install -y mysql-client

docker exec "$NEXTCLOUD_MYSQL" mysqldump --single-transaction -h localhost -u nextcloud -pnextcloud <TODO> > $ARCHIVE_DIR/nextcloud/db/nextcloud.bak

docker exec "$NEXTCLOUD_CONTAINER" /var/www/html/occ maintenance:mode --off

# === POSTGRES BACKUP ===
echo "[INFO] Backing up postgres databases..."
for db in "${PG_DBS[@]}"; do
    echo "[INFO] Backing up database $db..."
    docker exec -u postgres "$POSTGRES_CONTAINER" pg_dump -U "$PG_USER" -Fc "$db" > "$ARCHIVE_DIR/postgres/$db.dump"
    if [ $? -ne 0 ]; then
    echo "[ERROR] PostgreSQL backup failed"
    fi
done



# === BACKUP SPECIFIC HOST FOLDERS ===
echo "[INFO] Backing up specific host folders..."
for folder in "${FOLDERS_TO_BACKUP[@]}"; do
    echo "[INFO] Backing up $folder..."
    rsync -a "$folder" "$ARCHIVE_DIR/folders/"
done

# === COMPRESS BACKUP ===
echo "[INFO] Compressing backup..."
tar -czf "$ARCHIVE_FILE" -C "$BACKUP_DIR" "$TIMESTAMP"

# Remove the uncompressed backup directory
rm -rf "$ARCHIVE_DIR"

# === RSYNC TO REMOTE DEVICE ===
echo "[INFO] Syncing backups to remote device..."
if rsync -az -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" "$ARCHIVE_FILE" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"; then
    echo "[INFO] Transfer successful. Deleting local archive..."
    rm -f "$ARCHIVE_FILE"
else
    echo "[ERROR] failed"
    exit 1
fi


echo "[INFO] Backup completed successfully."
