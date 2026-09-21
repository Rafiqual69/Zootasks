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
    MessageHandler,
    filters,
)

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from asgiref.sync import sync_to_async
from accounts.models import WorkerProfile
from tasks.models import Task, TaskClaim
from wallet.models import WalletTransaction, WithdrawalRequest
from decimal import Decimal, InvalidOperation
from django.db.models import F


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
                "id",
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

        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)

        return

    lines = ["📋 উপলব্ধ কাজ:\n"]
    keyboard = []

    for task in tasks_list:
        lines.append(
            f"🔹 {task['title']}\n"
            f"💰 Reward: ৳{task['reward']}\n"
            f"👥 Workers: {task['completed_workers']}/{task['max_workers']}\n"
            f"📂 Category: {task['category']}\n"
        )

        keyboard.append([
            InlineKeyboardButton(
                f"👉 Claim: {task['title'][:25]}",
                callback_data=f"claim:{task['id']}",
            )
        ])

    text = "\n".join(lines)

    markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(
            text=text,
            reply_markup=markup,
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=markup,
        )


async def claim_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split(":")[1])
    telegram_user = update.effective_user

    @sync_to_async
    def do_claim():
        username = telegram_user.username or f"tg_{telegram_user.id}"

        user, _ = User.objects.get_or_create(
            username=username[:150],
            defaults={
                "first_name": telegram_user.first_name or "",
                "last_name": telegram_user.last_name or "",
            },
        )

        WorkerProfile.objects.get_or_create(user=user)

        try:
            with transaction.atomic():
                task = (
                    Task.objects
                    .select_for_update()
                    .get(id=task_id, status="active")
                )

                if task.completed_workers >= task.max_workers:
                    return "❌ এই task-এর worker limit পূর্ণ হয়ে গেছে।"

                if TaskClaim.objects.filter(
                    task=task,
                    worker=user,
                ).exists():
                    return "⚠️ আপনি এই task ইতিমধ্যে claim করেছেন।"

                TaskClaim.objects.create(
                    task=task,
                    worker=user,
                    status="claimed",
                )

                task.completed_workers += 1
                if task.completed_workers >= task.max_workers:
                    task.status = "completed"

                task.save(
                    update_fields=["completed_workers", "status"]
                )

        except Task.DoesNotExist:
            return "❌ এই task আর available নেই।"

        return (
            "✅ Task successfully claimed!\n\n"
            f"📋 {task.title}\n"
            f"💰 Reward: ৳{task.reward}\n\n"
            "📝 এখন আপনার proof submit করতে হবে।"
        )

    result = await do_claim()

    await query.edit_message_text(result)


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



async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_username = update.effective_user.username or f"tg_{update.effective_user.id}"

    user, created = await sync_to_async(User.objects.get_or_create)(
        username=telegram_username[:150],
        defaults={
            "first_name": update.effective_user.first_name or "",
            "last_name": update.effective_user.last_name or "",
        },
    )

    if created:
        user.set_unusable_password()
        await sync_to_async(user.save)()

    await sync_to_async(WorkerProfile.objects.get_or_create)(
        user=user
    )

    earned = await sync_to_async(
        lambda: WalletTransaction.objects.filter(
            user=user, transaction_type="earning"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )()

    withdrawn = await sync_to_async(
        lambda: WalletTransaction.objects.filter(
            user=user, transaction_type="withdrawal"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )()

    pending = await sync_to_async(
        lambda: WithdrawalRequest.objects.filter(
            user=user, status="pending"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )()

    available = earned - withdrawn - pending

    if available < Decimal("50.00"):
        await update.message.reply_text(
            f"❌ Minimum withdrawal ৳50.00.\n\n"
            f"💰 Available balance: ৳{available:.2f}"
        )
        return

    context.user_data["withdraw_step"] = "amount"

    await update.message.reply_text(
        f"💸 Withdrawal Request\n\n"
        f"💰 Available: ৳{available:.2f}\n"
        f"📌 Minimum: ৳50.00\n\n"
        f"আপনি কত টাকা withdraw করতে চান?\n"
        f"শুধু amount লিখুন।"
    )


async def withdrawal_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("withdraw_step")

    if step not in {"amount", "bank", "holder", "account"}:
        return False

    telegram_username = update.effective_user.username or f"tg_{update.effective_user.id}"

    user, created = await sync_to_async(User.objects.get_or_create)(
        username=telegram_username[:150],
        defaults={
            "first_name": update.effective_user.first_name or "",
            "last_name": update.effective_user.last_name or "",
        },
    )

    if created:
        user.set_unusable_password()
        await sync_to_async(user.save)()

    await sync_to_async(WorkerProfile.objects.get_or_create)(
        user=user
    )

    text = update.message.text.strip()

    if step == "amount":
        try:
            amount = Decimal(text)
        except (InvalidOperation, TypeError):
            await update.message.reply_text(
                "❌ সঠিক amount দিন। যেমন: 50"
            )
            return True

        profile = await sync_to_async(
            lambda: WorkerProfile.objects.get(user=user)
        )()

        available = profile.balance - profile.reserved_balance

        if amount < Decimal("50.00"):
            await update.message.reply_text(
                "❌ Minimum withdrawal ৳50.00."
            )
            return True

        if amount > available:
            await update.message.reply_text(
                f"❌ Insufficient balance.\n"
                f"Available: ৳{available:.2f}"
            )
            return True

        context.user_data["withdraw_amount"] = str(amount)
        context.user_data["withdraw_step"] = "bank"

        await update.message.reply_text(
            "🏦 Bank/MFS নাম লিখুন।\n"
            "যেমন: bKash / Nagad / Bank"
        )
        return True

    if step == "bank":
        context.user_data["withdraw_bank"] = text
        context.user_data["withdraw_step"] = "holder"

        await update.message.reply_text(
            "👤 Account holder-এর নাম লিখুন।"
        )
        return True

    if step == "holder":
        context.user_data["withdraw_holder"] = text
        context.user_data["withdraw_step"] = "account"

        await update.message.reply_text(
            "📱 Bank/MFS account number লিখুন।"
        )
        return True

    if step == "account":
        amount = Decimal(context.user_data["withdraw_amount"])
        bank = context.user_data["withdraw_bank"]
        holder = context.user_data["withdraw_holder"]

        @sync_to_async
        def create_withdrawal():
            with transaction.atomic():
                profile = (
                    WorkerProfile.objects
                    .select_for_update()
                    .get(user=user)
                )

                reserved = (
                    WorkerProfile.objects
                    .filter(
                        user=user,
                        balance__gte=F("reserved_balance") + amount,
                    )
                    .update(
                        reserved_balance=F("reserved_balance") + amount
                    )
                )

                if not reserved:
                    return None

                return WithdrawalRequest.objects.create(
                    user=user,
                    amount=amount,
                    bank_name=bank,
                    account_holder=holder,
                    bank_account=text,
                )

        withdrawal = await create_withdrawal()

        if withdrawal is None:
            context.user_data.clear()
            await update.message.reply_text(
                "❌ এই মুহূর্তে পর্যাপ্ত available balance নেই।\n"
                "দয়া করে আবার চেষ্টা করুন।"
            )
            return True

        context.user_data.clear()

        await update.message.reply_text(
            f"✅ Withdrawal request submitted!\n\n"
            f"🆔 Request: #{withdrawal.id}\n"
            f"💰 Amount: ৳{amount:.2f}\n"
            f"🏦 Method: {bank}\n"
            f"📌 Status: Pending\n\n"
            f"Admin review করার পর payment process হবে।"
        )
        return True

    return False

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
/myclaims - 📋 আপনার claimed tasks
/withdraw - 💸 Withdrawal request
/status - 📊 Bot status
/adminclaims - 🛡️ Admin claim review
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


async def submit_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    proof_text = update.message.text.strip()

    @sync_to_async
    def save_proof():
        username = telegram_user.username or f"tg_{telegram_user.id}"

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return "❌ আপনার ZooTasks account পাওয়া যায়নি। আগে /start দিন।"

        claim = (
            TaskClaim.objects
            .filter(
                worker=user,
                status="claimed",
            )
            .select_related("task")
            .order_by("-claimed_at")
            .first()
        )

        if not claim:
            return "❌ আপনার কোনো pending claimed task নেই।"

        claim.proof = proof_text
        claim.status = "submitted"
        claim.submitted_at = django.utils.timezone.now()
        claim.save(
            update_fields=["proof", "status", "submitted_at"]
        )

        return (
            "✅ Proof successfully submitted!\\n\\n"
            f"📋 Task: {claim.task.title}\\n"
            "⏳ Status: Admin review pending\\n\\n"
            "Admin approve করলে reward আপনার balance-এ যোগ হবে।"
        )

    result = await save_proof()
    await update.message.reply_text(result)


async def myclaims(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user

    @sync_to_async
    def get_claims():
        username = telegram_user.username or f"tg_{telegram_user.id}"

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return []

        return list(
            TaskClaim.objects
            .filter(worker=user, status="claimed")
            .select_related("task")
            .values("id", "task__title", "task__reward")
            .order_by("-claimed_at")[:10]
        )

    claims = await get_claims()

    if not claims:
        await update.message.reply_text(
            "❌ আপনার কোনো pending claimed task নেই।"
        )
        return

    text = "📝 আপনার Claimed Tasks:\\n\\n"

    for claim in claims:
        text += (
            f"🆔 Claim ID: {claim['id']}\\n"
            f"📋 {claim['task__title']}\\n"
            f"💰 Reward: ৳{claim['task__reward']}\\n\\n"
        )

    text += (
        "Proof submit করতে আপনার proof message হিসেবে পাঠান।\\n"
        "সর্বশেষ claimed task-এ proof যুক্ত হবে।"
    )

    await update.message.reply_text(text)


ADMIN_USERNAMES = {"admin", "arisha", "rafiqual"}


async def adminclaims(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    username = telegram_user.username or ""

    if username not in ADMIN_USERNAMES:
        await update.message.reply_text("❌ এই command শুধু Admin ব্যবহার করতে পারবে।")
        return

    @sync_to_async
    def get_pending_claims():
        return list(
            TaskClaim.objects
            .filter(status="submitted")
            .select_related("task", "worker")
            .values(
                "id",
                "task__title",
                "task__reward",
                "worker__username",
                "proof",
            )
            .order_by("submitted_at")[:20]
        )

    claims = await get_pending_claims()

    if not claims:
        await update.message.reply_text("✅ কোনো pending submission নেই।")
        return

    for claim in claims:
        text = (
            "📝 Pending Submission\\n\\n"
            f"🆔 Claim ID: {claim['id']}\\n"
            f"👤 Worker: @{claim['worker__username']}\\n"
            f"📋 Task: {claim['task__title']}\\n"
            f"💰 Reward: ৳{claim['task__reward']}\\n\\n"
            f"📄 Proof:\\n{claim['proof']}"
        )

        keyboard = [[
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve:{claim['id']}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject:{claim['id']}"
            ),
        ]]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def review_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_user = update.effective_user
    username = telegram_user.username or ""

    if username not in ADMIN_USERNAMES:
        await query.edit_message_text("❌ শুধু Admin এই action করতে পারবে।")
        return

    action, claim_id = query.data.split(":")
    claim_id = int(claim_id)

    @sync_to_async
    def process_claim():
        try:
            with transaction.atomic():
                claim = (
                    TaskClaim.objects
                    .select_for_update()
                    .select_related("task", "worker")
                    .get(id=claim_id)
                )

                if claim.status != "submitted":
                    return (
                        f"⚠️ এই claim আগে থেকেই "
                        f"{claim.status} অবস্থায় আছে।"
                    )

                if action == "reject":
                    claim.status = "rejected"
                    claim.save(update_fields=["status"])
                    return f"❌ Claim #{claim.id} rejected হয়েছে।"

                if action == "approve":
                    profile, _ = (
                        WorkerProfile.objects
                        .select_for_update()
                        .get_or_create(user=claim.worker)
                    )

                    existing_tx = WalletTransaction.objects.filter(
                        task_claim=claim,
                        transaction_type="earning",
                    ).first()

                    if existing_tx:
                        claim.status = "approved"
                        claim.save(update_fields=["status"])
                        return (
                            f"✅ Claim #{claim.id} already credited ছিল।"
                        )

                    WalletTransaction.objects.create(
                        user=claim.worker,
                        amount=claim.task.reward,
                        transaction_type="earning",
                        description=f"Reward for: {claim.task.title}",
                        task_claim=claim,
                    )

                    profile.balance += claim.task.reward
                    profile.total_earned += claim.task.reward
                    profile.completed_tasks += 1
                    profile.save(
                        update_fields=[
                            "balance",
                            "total_earned",
                            "completed_tasks",
                        ]
                    )

                    claim.status = "approved"
                    claim.save(update_fields=["status"])

                    return (
                        f"✅ Claim #{claim.id} approved হয়েছে.\n\n"
                        f"💰 Reward ৳{claim.task.reward} "
                        f"worker-এর balance-এ যোগ হয়েছে।"
                    )

                return "❌ Invalid action."

        except TaskClaim.DoesNotExist:
            return "❌ Claim পাওয়া যায়নি।"

    result = await process_claim()
    await query.edit_message_text(result)


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("tasks", tasks))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("adminclaims", adminclaims))
app.add_handler(CommandHandler("myclaims", myclaims))
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("withdraw_step")

    if step in {"amount", "bank", "holder", "account"}:
        await withdrawal_message(update, context)
        return

    await submit_proof(update, context)


app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, text_router)
)


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


app.add_handler(
    CallbackQueryHandler(claim_task, pattern=r"^claim:\d+$")
)

app.add_handler(
    CallbackQueryHandler(review_claim, pattern=r"^(approve|reject):\d+$")
)

try:
    app.run_polling()

except KeyboardInterrupt:
    print("\\n❌ Bot বন্ধ করা হয়েছে")
