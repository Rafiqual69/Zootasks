#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

PROJECT_DIR="$HOME/ZooTasks"
BACKUP_DIR="$HOME/zootasks-backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

BACKUP_FILE="$BACKUP_DIR/zootasks-backup-$DATE.tar.gz"
DB_BACKUP_FILE="$BACKUP_DIR/db-$DATE.sqlite3"

TMP_BACKUP_FILE="$BACKUP_FILE.tmp"
TMP_DB_BACKUP_FILE="$DB_BACKUP_FILE.tmp"

# Backups are sensitive recovery assets.
umask 077

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

cd "$PROJECT_DIR"

cleanup() {
    rm -f -- "$TMP_BACKUP_FILE" "$TMP_DB_BACKUP_FILE"
}
trap cleanup ERR INT TERM

# Project/source archive.
# Never include secrets, databases, local backups, logs,
# virtual environments or Git metadata.
tar \
  --exclude='./backend/venv'  \
  --exclude='./venv' \
  --exclude='./venv-zootasks' \
  --exclude='./.git' \
  --exclude='./__pycache__' \
  --exclude='*/__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='*.bak*' \
  --exclude='*.backup*' \
  --exclude='*.before-*' \
  --exclude='*-backup*' \
  --exclude='*.sqlite3*' \
  --exclude='*.db*' \
  --exclude='*.log*' \
  -czf "$TMP_BACKUP_FILE" .

chmod 600 "$TMP_BACKUP_FILE"
mv -f -- "$TMP_BACKUP_FILE" "$BACKUP_FILE"

# Database is a separate sensitive recovery asset.
if [ -f "$PROJECT_DIR/backend/db.sqlite3" ]; then
    cp -- "$PROJECT_DIR/backend/db.sqlite3" "$TMP_DB_BACKUP_FILE"
    chmod 600 "$TMP_DB_BACKUP_FILE"
    mv -f -- "$TMP_DB_BACKUP_FILE" "$DB_BACKUP_FILE"
else
    DB_BACKUP_FILE=""
fi

echo "======================================"
echo "ZooTasks Backup Completed"
echo "======================================"
echo "Backup file:"
echo "$BACKUP_FILE"

if [ -n "$DB_BACKUP_FILE" ]; then
    echo
    echo "Database backup:"
    echo "$DB_BACKUP_FILE"
else
    echo
    echo "Database backup:"
    echo "No backend/db.sqlite3 found"
fi
