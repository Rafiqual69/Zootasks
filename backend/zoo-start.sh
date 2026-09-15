#!/data/data/com.termux/files/usr/bin/bash

PROJECT_DIR="$HOME/taskbazar-pro"
BACKEND_DIR="$PROJECT_DIR/backend"

cd "$BACKEND_DIR" || exit 1
source ../venv/bin/activate

echo "============================================================"
echo "          ZOOTASKS SAFE STARTUP MANAGER"
echo "============================================================"

echo
echo "🔍 Checking Django server..."

if pgrep -f "manage.py runserver 0.0.0.0:8000" >/dev/null; then
    echo "✅ Django server already running"
else
    echo "🚀 Starting Django server..."
    nohup python manage.py runserver 0.0.0.0:8000 \
        > "$PROJECT_DIR/django.log" 2>&1 &
    echo "✅ Django server started"
fi

echo
echo "🔍 Checking Telegram bot..."

if pgrep -f "python run_bot.py" >/dev/null; then
    echo "✅ Telegram bot already running"
else
    echo "🤖 Starting Telegram bot..."
    nohup python run_bot.py \
        > "$PROJECT_DIR/bot.log" 2>&1 &
    echo "✅ Telegram bot started"
fi

echo
echo "📊 Running processes:"
pgrep -af "manage.py runserver|python run_bot.py" || true

echo
echo "============================================================"
echo "✅ ZOOTASKS STARTUP CHECK COMPLETED"
echo "============================================================"
echo
echo "Django log: $PROJECT_DIR/django.log"
echo "Bot log:    $PROJECT_DIR/bot.log"
