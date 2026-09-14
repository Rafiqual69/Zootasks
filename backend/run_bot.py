import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from users.models import CustomUser, Wallet
from tasks.models import Task

print("\n" + "="*60)
print("🤖 ZooTasks TELEGRAM BOT SETUP")
print("="*60 + "\n")

BOT_TOKEN = input("🔑 আপনার Telegram Bot Token পেস্ট করুন:\n➤ ").strip()

if not BOT_TOKEN or len(BOT_TOKEN) < 20:
    print("❌ Invalid Token!")
    exit()

print("\n✅ Token গৃহীত হয়েছে")
print("🔌 Bot সংযোগ করছে...\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 কাজ দেখুন", callback_data="tasks")],
        [InlineKeyboardButton("💰 ব্যালেন্স", callback_data="balance")],
        [InlineKeyboardButton("📞 যোগাযোগ", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """🎉 স্বাগতম ZooTasks এ!

আমরা একটি ফ্রিল্যান্স মার্কেটপ্লেস:
✅ কাজ পোস্ট করুন
✅ কাজের জন্য বিড করুন
✅ অর্থ উপার্জন করুন
✅ রেটিং পান

📞 Owner: +8801717831365
🌐 Website: http://localhost:8000/admin"""
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tasks_list = Task.objects.filter(status='open')
    if not tasks_list.exists():
        text = "❌ এখনো কোনো কাজ নেই"
        await query.edit_message_text(text)
        return
    
    text = "📋 উপলব্ধ কাজ:\n\n"
    for t in tasks_list:
        text += f"🔹 {t.title}\n   বাজেট: ৳{t.budget_bdt}\n   নিয়োগকর্তা: {t.employer.username}\n\n"
    
    await query.edit_message_text(text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        user = CustomUser.objects.get(username='worker1')
        wallet = user.wallet
        text = f"""💰 আপনার ব্যালেন্স:

💵 BDT: ৳{wallet.balance_bdt}
🏦 মোট উপার্জন: ৳{user.total_earnings}
⭐ রেটিং: {user.rating}/5"""
        await query.edit_message_text(text)
    except:
        text = "❌ অ্যাকাউন্ট পাওয়া যায়নি"
        await query.edit_message_text(text)

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """📞 যোগাযোগ তথ্য:

👤 Owner: EH Munna
📱 Phone: +8801717831365
💬 Telegram: @ZooTasksBot
📧 Email: rafiqual69@gmail.com

ব্যবসায়িক প্রস্তাবের জন্য যোগাযোগ করুন!"""
    
    await query.edit_message_text(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """❓ সাহায্য:

/start - বোট শুরু করুন
/tasks - সব কাজ দেখুন
/balance - ব্যালেন্স চেক করুন
/help - এই বার্তা
/status - বোট স্ট্যাটাস"""
    await update.message.reply_text(text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_count = CustomUser.objects.count()
    tasks_count = Task.objects.count()
    text = f"""🤖 বোট স্ট্যাটাস:

✅ Status: ONLINE
👥 Total Users: {users_count}
📋 Total Tasks: {tasks_count}
💳 Total Transactions: {Payment.objects.count() if 'Payment' in dir() else 'N/A'}"""
    await update.message.reply_text(text)

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("status", status))
app.add_handler(CallbackQueryHandler(tasks, pattern="^tasks$"))
app.add_handler(CallbackQueryHandler(balance, pattern="^balance$"))
app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))

print("="*60)
print("✅ TELEGRAM BOT READY")
print("="*60)
print("\n🤖 Bot Status: RUNNING ✓")
print("📞 Owner: +8801717831365")
print("🔌 Token: " + BOT_TOKEN[:20] + "...")
print("\n📋 Available Commands:")
print("   /start - শুরু করুন")
print("   /tasks - কাজ দেখুন")
print("   /balance - ব্যালেন্স")
print("   /status - বোট স্ট্যাটাস")
print("   /help - সাহায্য")
print("\n" + "="*60)
print("Press Ctrl+C to stop the bot")
print("="*60 + "\n")

try:
    app.run_polling()
except KeyboardInterrupt:
    print("\n\n❌ Bot বন্ধ করা হয়েছে")

