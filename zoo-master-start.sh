#!/data/data/com.termux/files/usr/bin/bash

set -u

PROJECT_DIR="$HOME/ZooTasks"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV="$PROJECT_DIR/venv"

DJANGO_LOG="$PROJECT_DIR/django.log"
BOT_LOG="$PROJECT_DIR/bot.log"

echo "============================================================"
echo "              🦁 ZOOTASKS MASTER START"
echo "============================================================"

# ------------------------------------------------------------
# 1. Project check
# ------------------------------------------------------------

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ ZooTasks project not found."
    exit 1
fi

if [ ! -d "$VENV" ]; then
    echo "❌ Virtual environment not found."
    exit 1
fi

if [ ! -f "$BACKEND_DIR/manage.py" ]; then
    echo "❌ Django manage.py not found."
    exit 1
fi

cd "$BACKEND_DIR" || exit 1

# ------------------------------------------------------------
# 2. Activate virtual environment
# ------------------------------------------------------------

source "$VENV/bin/activate"

echo
echo "🐍 Python:"
python --version

# ------------------------------------------------------------
# 3. Django health check
# ------------------------------------------------------------

echo
echo "🔍 Django health check..."

python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Django check failed."
    exit 1
fi

echo "✅ Django check passed."

# ------------------------------------------------------------
# 4. Database migration check
# ------------------------------------------------------------

echo
echo "🗄️ Checking migrations..."

python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo "❌ Migration failed."
    exit 1
fi

echo "✅ Database ready."

# ------------------------------------------------------------
# 5. Start Django only if not already running
# ------------------------------------------------------------

echo
echo "🌐 Checking Django server..."

if pgrep -f "manage.py runserver 0.0.0.0:8000" >/dev/null 2>&1; then
    echo "✅ Django server already running."
else
    echo "🚀 Starting Django server..."

    nohup python manage.py runserver 0.0.0.0:8000 \
        > "$DJANGO_LOG" 2>&1 &

    sleep 3

    if pgrep -f "manage.py runserver 0.0.0.0:8000" >/dev/null 2>&1; then
        echo "✅ Django server started."
    else
        echo "❌ Django server failed to start."
        tail -n 30 "$DJANGO_LOG" 2>/dev/null || true
        exit 1
    fi
fi

# ------------------------------------------------------------
# 6. Start Telegram bot only if not already running
# ------------------------------------------------------------

echo
echo "🤖 Checking Telegram bot..."

if pgrep -f "python run_bot.py" >/dev/null 2>&1; then
    echo "✅ Telegram bot already running."
else
    echo "🚀 Starting Telegram bot..."

    nohup python run_bot.py \
        > "$BOT_LOG" 2>&1 &

    sleep 5

    if pgrep -f "python run_bot.py" >/dev/null 2>&1; then
        echo "✅ Telegram bot started."
    else
        echo "❌ Telegram bot failed to start."
        tail -n 40 "$BOT_LOG" 2>/dev/null || true
        exit 1
    fi
fi

# ------------------------------------------------------------
# 7. Local HTTP health check
# ------------------------------------------------------------

echo
echo "🌍 Checking website..."

if command -v curl >/dev/null 2>&1; then
    if curl -s --max-time 10 \
        -o /dev/null \
        -w "%{http_code}" \
        http://127.0.0.1:8000/ | grep -qE "200|301|302"; then

        echo "✅ Website responding on port 8000."
    else
        echo "⚠️ Website process exists, but HTTP check failed."
    fi
else
    echo "ℹ️ curl not installed; skipped HTTP check."
fi

# ------------------------------------------------------------
# 8. Final status
# ------------------------------------------------------------

echo
echo "============================================================"
echo "                 🦁 ZOOTASKS STATUS"
echo "============================================================"

echo
echo "📁 Project:"
echo "$PROJECT_DIR"

echo
echo "🌐 Django:"
if pgrep -f "manage.py runserver 0.0.0.0:8000" >/dev/null 2>&1; then
    echo "🟢 RUNNING"
else
    echo "🔴 STOPPED"
fi

echo
echo "🤖 Telegram Bot:"
if pgrep -f "python run_bot.py" >/dev/null 2>&1; then
    echo "🟢 RUNNING"
else
    echo "🔴 STOPPED"
fi

echo
echo "📋 Logs:"
echo "Django → $DJANGO_LOG"
echo "Bot    → $BOT_LOG"

echo
echo "🌐 Website:"
echo "http://127.0.0.1:8000/"

echo
echo "🛠️ Admin:"
echo "http://127.0.0.1:8000/admin/"

echo
echo "============================================================"
echo "          ✅ ZOOTASKS MASTER START COMPLETE"
echo "============================================================"
