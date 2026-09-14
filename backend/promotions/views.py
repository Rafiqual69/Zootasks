from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import Promotion, PromotionClaim
from wallet.models import WalletTransaction

@login_required
def marketplace(request):
    promotions = Promotion.objects.filter(status="approved").order_by("-created_at")
    search = request.GET.get("search", "").strip()
    if search:
        promotions = promotions.filter(title__icontains=search)
    cards = ""
    for promotion in promotions:
        claim = PromotionClaim.objects.filter(promotion=promotion, worker=request.user).first()
        remaining = max(promotion.max_workers - promotion.completed_workers, 0)
        if claim:
            if claim.status == "claimed":
                action = f'<a class="btn-action" href="/promotions/{promotion.id}/submit/">📤 Submit Proof</a>'
            elif claim.status == "submitted":
                action = '<div class="status-badge waiting">⏳ Under Review</div>'
            elif claim.status == "approved":
                action = '<div class="status-badge success">✅ Approved</div>'
            else:
                action = '<div class="status-badge danger">❌ Rejected</div>'
        elif remaining > 0:
            action = f'<form method="post" action="/promotions/{promotion.id}/start/" style="margin:0"><input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get("CSRF_COOKIE", "")}"><button class="btn-action" type="submit">🎯 Start Now</button></form>'
        else:
            action = '<div class="status-badge">🔒 Full</div>'
        progress = (promotion.completed_workers / max(promotion.max_workers, 1)) * 100
        cards += f"""<div class="promo-card">
            <div class="promo-header">
                <div><h3>{promotion.title}</h3><p class="promo-advertiser">by {promotion.advertiser_name}</p></div>
                <div class="promo-reward">৳{promotion.reward}</div>
            </div>
            <p class="promo-desc">{promotion.description[:100]}...</p>
            <div class="progress-bar"><div class="progress-fill" style="width:{progress}%"></div></div>
            <p class="progress-text">{promotion.completed_workers}/{promotion.max_workers} workers</p>
            <div class="promo-action">{action}</div>
        </div>"""
    if not cards:
        cards = '<div class="empty-state"><h2>📭 No promotions</h2></div>'
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Promotions - ZooTasks</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:#f8fafc;color:#0f172a}}header{{background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;padding:16px 0;position:sticky;top:0}}header .container{{max-width:1200px;margin:0 auto;padding:0 16px;display:flex;justify-content:space-between;align-items:center}}.logo{{font-size:20px;font-weight:bold}}.header-nav{{display:flex;gap:20px}}.header-nav a{{color:white;text-decoration:none;opacity:.9}}.header-nav a:hover{{opacity:1}}.container{{max-width:1200px;margin:0 auto;padding:0 16px}}.hero{{background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;padding:40px 16px;text-align:center}}.hero h1{{font-size:32px;margin-bottom:12px}}.search-box{{max-width:500px;margin:20px auto;display:flex;gap:10px}}.search-box input{{flex:1;padding:12px;border:none;border-radius:10px}}.search-box button{{padding:12px 24px;background:rgba(255,255,255,.2);color:white;border:2px solid white;border-radius:10px;cursor:pointer}}.search-box button:hover{{background:white;color:#2563eb}}.content{{padding:40px 16px}}.promos-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;margin-top:30px}}.promo-card{{background:white;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.08);border:1px solid #e2e8f0;transition:transform .2s}}.promo-card:hover{{transform:translateY(-4px);box-shadow:0 12px 24px rgba(0,0,0,.12)}}.promo-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px}}.promo-header h3{{font-size:18px;margin-bottom:4px}}.promo-reward{{font-size:24px;font-weight:bold;color:#16a34a}}.promo-desc{{color:#64748b;font-size:14px;margin-bottom:16px}}.progress-bar{{height:8px;background:#e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:8px}}.progress-fill{{height:100%;background:linear-gradient(90deg,#2563eb,#7c3aed)}}.progress-text{{font-size:12px;color:#94a3b8;margin-bottom:16px}}.btn-action{{width:100%;padding:12px;background:#2563eb;color:white;border:none;border-radius:10px;font-weight:600;cursor:pointer;transition:all .2s}}.btn-action:hover{{background:#1d4ed8}}.status-badge{{padding:8px 12px;border-radius:8px;font-size:12px;font-weight:600;text-align:center}}.status-badge.waiting{{background:#fef3c7;color:#92400e}}.status-badge.success{{background:#dcfce7;color:#166534}}.status-badge.danger{{background:#fee2e2;color:#991b1b}}.empty-state{{text-align:center;padding:60px 20px;color:#94a3b8}}@media(max-width:768px){{.promos-grid{{grid-template-columns:1fr}}}}</style>
</head><body>
<header><div class="container"><div class="logo">🦁 ZooTasks</div><div class="header-nav"><a href="/accounts/dashboard/">Dashboard</a><a href="/tasks/">Tasks</a><a href="/">Home</a></div></div></header>
<div class="hero"><div class="container"><h1>🎯 Promotions</h1><form method="get" class="search-box"><input type="text" name="search" placeholder="Search..." value="{search}"><button type="submit">Search</button></form></div></div>
<div class="content"><div class="container"><div class="promos-grid">{cards}</div></div></div>
</body></html>"""
    return HttpResponse(html)

@login_required
@transaction.atomic
def start_promotion(request, promotion_id):
    if request.method != "POST":
        return redirect("promotion_marketplace")
    promotion = get_object_or_404(Promotion.objects.select_for_update(), id=promotion_id, status="approved")
    existing = PromotionClaim.objects.filter(promotion=promotion, worker=request.user).first()
    if existing or promotion.completed_workers >= promotion.max_workers:
        return redirect("promotion_marketplace")
    PromotionClaim.objects.create(promotion=promotion, worker=request.user)
    promotion.completed_workers += 1
    if promotion.completed_workers >= promotion.max_workers:
        promotion.status = "paused"
    promotion.save(update_fields=["completed_workers", "status"])
    return redirect("promotion_marketplace")

@login_required
def submit_promotion(request, promotion_id):
    claim = get_object_or_404(PromotionClaim, promotion_id=promotion_id, worker=request.user)
    if claim.status != "claimed":
        return redirect("promotion_marketplace")
    if request.method == "POST":
        proof = request.POST.get("proof", "").strip()
        if proof:
            claim.proof = proof
            claim.status = "submitted"
            claim.submitted_at = timezone.now()
            claim.save(update_fields=["proof", "status", "submitted_at"])
            return redirect("promotion_marketplace")
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Submit - ZooTasks</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:linear-gradient(135deg,#f8fafc,#e0e7ff);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}.box{{background:white;border-radius:20px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,.15);max-width:600px;width:100%}}.box h1{{font-size:28px;margin-bottom:8px;color:#2563eb}}.box h2{{font-size:20px;color:#0f172a;margin-bottom:12px;margin-top:24px}}.box p{{color:#64748b;margin-bottom:20px;line-height:1.6}}textarea{{width:100%;min-height:160px;padding:16px;border:2px solid #e2e8f0;border-radius:12px;font-family:inherit;font-size:14px}}textarea:focus{{outline:none;border-color:#2563eb}}button{{width:100%;padding:14px;background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;border:none;border-radius:12px;font-weight:600;font-size:16px;cursor:pointer;margin-top:20px;transition:transform .2s,box-shadow .2s}}button:hover{{transform:translateY(-2px);box-shadow:0 10px 20px rgba(37,99,235,.3)}}</style>
</head><body>
<div class="box"><h1>📤 Submit Proof</h1><h2>{claim.promotion.title}</h2><p>{claim.promotion.description}</p>
<form method="post"><input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get("CSRF_COOKIE", "")}"><textarea name="proof" placeholder="Describe completion..." required></textarea><button type="submit">✓ Submit</button></form></div>
</body></html>"""
    return HttpResponse(html)
