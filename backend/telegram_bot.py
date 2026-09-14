import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from accounts.models import CustomUser, Wallet
from tasks.models import Task

BOT_TOKEN = '7584827421:AAH-Iqh5QX_7bLjKJLq9E8m9_7Y_nB0Zs6c'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 কাজ দেখুন", callback_data="tasks_list")],
        [InlineKeyboardButton("💰 ব্যালেন্স", callback_data="my_balance")],
        [InlineKeyboardButton("📞 যোগাযোগ", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """🎉 স্বাগতম ZooTasks এ!

আমরা একটি ফ্রিল্যান্স মার্কেটপ্লেস যেখানে আপনি:
✅ কাজ পোস্ট করতে পারেন
✅ কাজের জন্য বিড করতে পারেন
✅ অর্থ উপার্জন করতে পারেন
✅ রেটিং পেতে পারেন

📞 Owner: +8801717831365
💼 বেশি তথ্যের জন্য মেনু দেখুন"""
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def tasks_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tasks = Task.objects.filter(status='open')
    if not tasks.exists():
        text = "❌ এখনো কোনো কাজ নেই"
        await query.edit_message_text(text)
        return
    
    text = "📋 উপলব্ধ কাজ:\n\n"
    for t in tasks:
        text += f"🔹 {t.title}\n   বাজেট: ৳{t.budget_bdt}\n   নিয়োগকর্তা: {t.employer.username}\n\n"
    
    await query.edit_message_text(text)

async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """❓ সাহায্য:

/start - বোট শুরু করুন
/tasks - সব কাজ দেখুন
/balance - ব্যালেন্স চেক করুন
/help - এই বার্তা

🎯 কমান্ড:
/register - রেজিস্টার করুন
/withdraw - টাকা উত্তোলন করুন
/support - সাপোর্ট"""
    
    await update.message.reply_text(text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(tasks_list, pattern="^tasks_list$"))
    app.add_handler(CallbackQueryHandler(my_balance, pattern="^my_balance$"))
    app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    
    print("\n" + "="*60)
    print("✅ TELEGRAM BOT STARTED")
    print("="*60)
    print("\n🤖 Bot Status: RUNNING")
    print("👤 Bot: @ZooTasksBot")
    print("🔌 Token: " + BOT_TOKEN[:20] + "...")
    print("\n📋 Commands:")
    print("   /start - শুরু করুন")
    print("   /tasks - কাজ দেখুন")
    print("   /balance - ব্যালেন্স")
    print("   /help - সাহায্য")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the bot")
    print("="*60 + "\n")
    
    app.run_polling()

if __name__ == '__main__':
    main()
