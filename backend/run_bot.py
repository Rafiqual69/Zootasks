import os
from pathlib import Path
from dotenv import load_dotenv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
load_dotenv(Path(__file__).resolve().parent / '.env')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from accounts.models import WorkerProfile
from tasks.models import Task


print("\n" + "=" * 60)
print("🤖 ZooTasks TELEGRAM BOT")
print("=" * 60 + "\n")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN or len(BOT_TOKEN) < 20:
    print("❌ Invalid Token!")
    raise SystemExit(1)

print("\n✅ Token গ্রহণ করা হয়েছে")
print("🔌 Bot সংযোগ করছে...\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user

    @sync_to_async
    def create_account():
        username = telegram_user.username or f"tg_{telegram_user.id}"

        user, _ = User.objects.get_or_create(
            username=username[:150],
            defaults={
                "first_name": telegram_user.first_name or "",
                "last_name": telegram_user.last_name or "",
            },
        )

        WorkerProfile.objects.get_or_create(user=user)

    await create_account()

    keyboard = [
        [
            InlineKeyboardButton("📋 কাজ দেখুন", callback_data="tasks"),
            InlineKeyboardButton("💰 ব্যালেন্স", callback_data="balance"),
        ],
        [
            InlineKeyboardButton("📊 আমার Progress", callback_data="status"),
        ],
        [
            InlineKeyboardButton("📞 যোগাযোগ", callback_data="contact"),
        ],
    ]

    text = """🎉 স্বাগতম ZooTasks-এ!

🚀 Work Smart. Complete Tasks. Earn Rewards.

✅ আপনার ZooTasks account তৈরি হয়েছে।

নিচের menu থেকে একটি option নির্বাচন করুন।"""

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query:
        await query.answer()

    @sync_to_async
    def get_tasks():
        return list(
            Task.objects.filter(status="active")
            .values(
                "title",
                "reward",
                "completed_workers",
                "max_workers",
                "category",
            )[:20]
        )

    tasks_list = await get_tasks()

    if not tasks_list:
        text = "❌ এখনো কোনো active কাজ নেই।"
    else:
        text = "📋 উপলব্ধ কাজ:\n\n"

        for task in tasks_list:
            text += (
                f"🔹 {task['title']}\n"
                f"💰 Reward: ৳{task['reward']}\n"
                f"👥 Workers: {task['completed_workers']}/{task['max_workers']}\n"
                f"📂 Category: {task['category']}\n\n"
            )

    if query:
        await query.edit_message_text(text)
    else:
        await update.message.reply_text(text)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query:
        await query.answer()

    telegram_user = update.effective_user

    @sync_to_async
    def get_balance():
        try:
            user = User.objects.get(username=telegram_user.username)
        except User.DoesNotExist:
            return None

        profile, _ = WorkerProfile.objects.get_or_create(user=user)

        return {
            "username": user.username,
            "balance": profile.balance,
            "total_earned": profile.total_earned,
            "completed_tasks": profile.completed_tasks,
        }

    data = await get_balance()

    if data is None:
        text = "❌ আপনার ZooTasks account এখনো তৈরি হয়নি।"
    else:
        text = f"""💰 আপনার ZooTasks Balance

💵 Balance: ৳{data['balance']}
🏦 Total Earned: ৳{data['total_earned']}
✅ Completed Tasks: {data['completed_tasks']}

👤 Username: @{data['username']}"""

    if query:
        await query.edit_message_text(text)
    else:
        await update.message.reply_text(text)


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = """📞 ZooTasks Support

👤 Owner: MD Rafiqual Islam
📱 Phone: +8801717831365
💬 Telegram: @ZooTasksBot
📧 Email: rafiqual69@gmail.com

ব্যবসায়িক প্রস্তাব বা support-এর জন্য যোগাযোগ করুন।"""

    await query.edit_message_text(text)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """❓ ZooTasks Help

/start - 🚀 Bot শুরু করুন
/tasks - 📋 Available tasks
/balance - 💰 Balance দেখুন
/status - 📊 Bot status
/help - ❓ Help"""

    await update.message.reply_text(text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    @sync_to_async
    def get_status():
        return (
            User.objects.count(),
            WorkerProfile.objects.count(),
            Task.objects.count(),
        )

    users_count, profiles_count, tasks_count = await get_status()

    text = f"""🤖 ZooTasks Bot Status

✅ Status: ONLINE

👥 Total Users: {users_count}
👤 Worker Profiles: {profiles_count}
📋 Total Tasks: {tasks_count}"""

    await update.message.reply_text(text)


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("tasks", tasks))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("status", status))

app.add_handler(
    CallbackQueryHandler(tasks, pattern="^tasks$")
)

app.add_handler(
    CallbackQueryHandler(balance, pattern="^balance$")
)

app.add_handler(
    CallbackQueryHandler(contact, pattern="^contact$")
)


print("=" * 60)
print("✅ ZOOTASKS TELEGRAM BOT READY")
print("=" * 60)
print("\n🤖 Bot Status: RUNNING ✓")
print("\n📋 Commands:")
print("   /start")
print("   /tasks")
print("   /balance")
print("   /status")
print("   /help")
print("\nPress Ctrl+C to stop the bot")
print("=" * 60 + "\n")


try:
    app.run_polling()

except KeyboardInterrupt:
    print("\n❌ Bot বন্ধ করা হয়েছে")

