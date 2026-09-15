#!/data/data/com.termux/files/usr/bin/bash
set -e

PROJECT_DIR="$HOME/ZooTasks"
BACKUP_DIR="$HOME/zootasks-backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/zootasks-backup-$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

cd "$PROJECT_DIR"

tar \
  --exclude='venv' \
  --exclude='venv-zootasks' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='db.sqlite3' \
  -czf "$BACKUP_FILE" .

if [ -f "$PROJECT_DIR/backend/db.sqlite3" ]; then
  cp "$PROJECT_DIR/backend/db.sqlite3" "$BACKUP_DIR/db-$DATE.sqlite3"
fi

echo "======================================"
echo "ZooTasks Backup Completed"
echo "======================================"
echo "Backup file:"
echo "$BACKUP_FILE"
echo
echo "Database backup:"
echo "$BACKUP_DIR/db-$DATE.sqlite3"
