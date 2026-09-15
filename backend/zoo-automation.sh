#!/data/data/com.termux/files/usr/bin/bash

set -u

PROJECT_DIR="$HOME/ZooTasks"
BACKEND_DIR="$PROJECT_DIR/backend"
BACKUP_DIR="$PROJECT_DIR/auto-backups"

echo "============================================================"
echo "        ZOOTASKS AUTOMATION MASTER CHECK"
echo "============================================================"

cd "$BACKEND_DIR" || {
    echo "❌ Backend directory পাওয়া যায়নি"
    exit 1
}

if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment পাওয়া যায়নি"
    exit 1
fi

source ../venv/bin/activate

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
DB_BACKUP="$BACKUP_DIR/db_$TIMESTAMP.sqlite3"

echo
echo "📦 Step 1: Database backup"

if [ -f db.sqlite3 ]; then
    cp db.sqlite3 "$DB_BACKUP"
    echo "✅ Database backup created:"
    echo "$DB_BACKUP"
else
    echo "⚠️ db.sqlite3 পাওয়া যায়নি"
fi

echo
echo "🔍 Step 2: Django system check"
python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Django check failed"
    exit 1
fi

echo
echo "🐍 Step 3: Python compile check"
python -m compileall -q accounts core main offers promotions tasks wallet config

if [ $? -ne 0 ]; then
    echo "❌ Python compile check failed"
    exit 1
fi

echo "✅ Python compile check passed"

echo
echo "🗃️ Step 4: Git status"
cd "$PROJECT_DIR"

git status --short

echo
echo "📊 Step 5: Backup count"
find "$BACKUP_DIR" -maxdepth 1 -type f | wc -l

echo
echo "============================================================"
echo "✅ AUTOMATION CHECK COMPLETED SUCCESSFULLY"
echo "============================================================"
echo
echo "ℹ️ এই script server বা bot চালু করেনি।"
echo "ℹ️ Duplicate process এড়াতে startup আলাদা ধাপে করা হবে।"
