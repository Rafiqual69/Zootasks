#!/data/data/com.termux/files/usr/bin/bash

PROJECT_DIR="$HOME/ZooTasks"
LOG_FILE="$PROJECT_DIR/task-scheduler.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Scheduler started" >> "$LOG_FILE"

bash "$PROJECT_DIR/zoo-task-generator.sh" >> "$LOG_FILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Scheduler finished" >> "$LOG_FILE"
