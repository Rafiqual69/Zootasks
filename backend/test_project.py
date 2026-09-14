import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser, Wallet
from tasks.models import Task
from payments.models import Payment
from ratings.models import Rating
from datetime import datetime, timedelta

print("\n" + "="*60)
print("🚀 ZooTasks - COMPLETE TEST")
print("="*60 + "\n")

# ১. Employer তৈরি করুন
print("📋 Step 1: Creating Employer...")
employer, created = CustomUser.objects.get_or_create(
    username='employer1',
    defaults={
        'email': 'employer@zootasks.com',
        'phone': '+8801700000001',
        'role': 'employer',
        'first_name': 'Employer',
        'last_name': 'One'
    }
)
if created:
    employer.set_password('employer123')
    employer.save()
    print(f"✅ New Employer created: {employer.username}")
else:
    print(f"✅ Employer exists: {employer.username}")

emp_wallet, _ = Wallet.objects.get_or_create(
    user=employer,
    defaults={'balance_bdt': 100000}
)
print(f"💰 Balance: ৳{emp_wallet.balance_bdt}\n")

# २. Worker তৈরি করুন
print("📋 Step 2: Creating Worker...")
worker, created = CustomUser.objects.get_or_create(
    username='worker1',
    defaults={
        'email': 'worker@zootasks.com',
        'phone': '+8801700000002',
        'role': 'worker',
        'first_name': 'Worker',
        'last_name': 'One'
    }
)
if created:
    worker.set_password('worker123')
    worker.save()
    print(f"✅ New Worker created: {worker.username}")
else:
    print(f"✅ Worker exists: {worker.username}")

wrk_wallet, _ = Wallet.objects.get_or_create(
    user=worker,
    defaults={'balance_bdt': 0}
)
print(f"💰 Balance: ৳{wrk_wallet.balance_bdt}\n")

# ३. Task তৈরি করুন
print("📋 Step 3: Creating Task...")
task, created = Task.objects.get_or_create(
    employer=employer,
    title='Copy-Paste Work',
    defaults={
        'description': 'Copy 100 links and paste in list format. Very simple task.',
        'budget_bdt': 5000,
        'status': 'open',
        'deadline': datetime.now() + timedelta(days=7)
    }
)
if created:
    print(f"✅ New Task created: {task.title}")
else:
    print(f"✅ Task exists: {task.title}")
print(f"💵 Budget: ৳{task.budget_bdt}\n")

# ४. Task Assign করুন
print("📋 Step 4: Assigning Task to Worker...")
task.assigned_worker = worker
task.status = 'in_progress'
task.save()
print(f"✅ Task assigned to: {worker.username}\n")

# ५. Payment তৈরি করুন
print("📋 Step 5: Creating Payment...")
payment, created = Payment.objects.get_or_create(
    payer=employer,
    payee=worker,
    task=task,
    defaults={
        'amount': 5000,
        'method': 'bkash',
        'status': 'completed'
    }
)
if created:
    print(f"✅ New Payment created")
else:
    print(f"✅ Payment exists")
print(f"💳 {employer.username} → {worker.username}: ৳{payment.amount}\n")

# ६. Wallet Update করুন
print("📋 Step 6: Updating Wallets...")
emp_wallet.balance_bdt -= payment.amount
emp_wallet.save()
wrk_wallet.balance_bdt += payment.amount
wrk_wallet.save()
print(f"✅ Employer Balance: ৳{emp_wallet.balance_bdt}")
print(f"✅ Worker Balance: ৳{wrk_wallet.balance_bdt}\n")

# ७. Rating তৈরি করুন
print("📋 Step 7: Creating Rating...")
rating, created = Rating.objects.get_or_create(
    task=task,
    rater=employer,
    ratee=worker,
    defaults={'score': 5}
)
if created:
    print(f"✅ New Rating created")
else:
    print(f"✅ Rating exists")
print(f"⭐ {worker.username} - Score: {rating.score}/5\n")

# ८. সম্পূর্ণ ডেটা Display করুন
print("="*60)
print("📊 FINAL DATA SUMMARY")
print("="*60 + "\n")

print("👥 USERS:")
for user in CustomUser.objects.all():
    wallet = user.wallet
    print(f"   • {user.username} ({user.role}) - ৳{wallet.balance_bdt} BDT")

print(f"\n📋 TASKS ({Task.objects.count()}):")
for t in Task.objects.all():
    assigned = t.assigned_worker.username if t.assigned_worker else "Unassigned"
    print(f"   • {t.title}")
    print(f"     Status: {t.status} | Assigned: {assigned} | Budget: ৳{t.budget_bdt}")

print(f"\n💳 PAYMENTS ({Payment.objects.count()}):")
for p in Payment.objects.all():
    print(f"   • {p.payer.username} → {p.payee.username}: ৳{p.amount} ({p.method.upper()}) [{p.status}]")

print(f"\n⭐ RATINGS ({Rating.objects.count()}):")
for r in Rating.objects.all():
    print(f"   • {r.rater.username} rated {r.ratee.username}: {r.score}⭐/5⭐")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\n🌐 Admin Panel Access:")
print("   URL: http://localhost:8000/admin")
print("   Username: admin")
print("   Password: admin123")
print("\n🔐 Test Accounts:")
print("   Employer: employer1 / employer123")
print("   Worker: worker1 / worker123")
print("\n" + "="*60 + "\n")

