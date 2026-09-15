#!/data/data/com.termux/files/usr/bin/bash

PROJECT_DIR="$HOME/ZooTasks"
BACKEND_DIR="$PROJECT_DIR/backend"
LOG_FILE="$PROJECT_DIR/task-generator.log"
LOCK_FILE="$PROJECT_DIR/.task-generator.lock"

if [ -e "$LOCK_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Already running. Exiting." >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"

cleanup() {
    rm -f "$LOCK_FILE"
}

trap cleanup EXIT

cd "$BACKEND_DIR" || exit 1
source "$PROJECT_DIR/venv/bin/activate" || exit 1

echo "==================================================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Task generator started" >> "$LOG_FILE"

python manage.py generate_tasks --limit 1 >> "$LOG_FILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Task generator finished" >> "$LOG_FILE"
