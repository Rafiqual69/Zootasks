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
print("🚀 ZooTasks TEST DATA CREATION")
print("="*60 + "\n")

emp, created = CustomUser.objects.get_or_create(username='employer1', defaults={'email': 'employer@test.com', 'phone': '+8801700000001', 'role': 'employer'})
if created: emp.set_password('employer123'); emp.save(); print("✅ Employer created: employer1 / employer123")
else: print("✅ Employer exists: employer1")

emp_wallet, _ = Wallet.objects.get_or_create(user=emp, defaults={'balance_bdt': 100000})
print(f"💰 Employer Balance: ৳{emp_wallet.balance_bdt}\n")

wrk, created = CustomUser.objects.get_or_create(username='worker1', defaults={'email': 'worker@test.com', 'phone': '+8801700000002', 'role': 'worker'})
if created: wrk.set_password('worker123'); wrk.save(); print("✅ Worker created: worker1 / worker123")
else: print("✅ Worker exists: worker1")

wrk_wallet, _ = Wallet.objects.get_or_create(user=wrk, defaults={'balance_bdt': 0})
print(f"💰 Worker Balance: ৳{wrk_wallet.balance_bdt}\n")

task, created = Task.objects.get_or_create(employer=emp, title='Copy-Paste Work', defaults={'description': 'Copy 100 links and paste in list format', 'budget_bdt': 5000, 'status': 'open', 'deadline': datetime.now() + timedelta(days=7)})
print(f"✅ Task created: {task.title}")
print(f"💵 Budget: ৳{task.budget_bdt}\n")

task.assigned_worker = wrk; task.status = 'in_progress'; task.save()
print(f"✅ Task assigned to: {wrk.username}\n")

payment, created = Payment.objects.get_or_create(payer=emp, payee=wrk, task=task, defaults={'amount': 5000, 'method': 'bkash', 'status': 'completed'})
print(f"✅ Payment created: {emp.username} → {wrk.username}: ৳{payment.amount}\n")

emp_wallet.balance_bdt -= 5000; emp_wallet.save()
wrk_wallet.balance_bdt += 5000; wrk_wallet.save()
print(f"✅ Wallets updated:\n   Employer: ৳{emp_wallet.balance_bdt}\n   Worker: ৳{wrk_wallet.balance_bdt}\n")

rating, created = Rating.objects.get_or_create(task=task, rater=emp, ratee=wrk, defaults={'score': 5})
print(f"✅ Rating created: {wrk.username} - ⭐{rating.score}/5\n")

print("="*60)
print("📊 FINAL DATA SUMMARY")
print("="*60 + "\n")
print("👥 USERS:"); [print(f"   • {u.username} ({u.role}) - ৳{u.wallet.balance_bdt} BDT") for u in CustomUser.objects.all()]
print(f"\n📋 TASKS ({Task.objects.count()}):"); [print(f"   • {t.title}\n     Status: {t.status} | Budget: ৳{t.budget_bdt}") for t in Task.objects.all()]
print(f"\n💳 PAYMENTS ({Payment.objects.count()}):"); [print(f"   • {p.payer.username} → {p.payee.username}: ৳{p.amount} ({p.method})") for p in Payment.objects.all()]
print(f"\n⭐ RATINGS ({Rating.objects.count()}):"); [print(f"   • {r.rater.username} rated {r.ratee.username}: ⭐{r.score}/5") for r in Rating.objects.all()]
print("\n" + "="*60)
print("✅ ALL TEST DATA CREATED!")
print("="*60)
print("\n🌐 ADMIN PANEL: http://localhost:8000/admin")
print("   Username: admin | Password: admin123")
print("\n📱 TEST ACCOUNTS:")
print("   Employer: employer1 / employer123")
print("   Worker: worker1 / worker123")
print("\n" + "="*60 + "\n")
