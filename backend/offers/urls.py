from django.urls import path
from django.http import HttpResponse

def marketplace(request):
    return HttpResponse("""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Offers Marketplace</title>
<style>
body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
.wrap{max-width:900px;margin:auto;padding:28px}
.hero{background:linear-gradient(135deg,#047857,#064e3b);color:white;padding:32px;border-radius:20px}
.card{background:white;padding:22px;border-radius:16px;margin-top:20px;box-shadow:0 4px 16px #0001}
.btn{display:inline-block;background:#047857;color:white;padding:12px 18px;border-radius:10px;text-decoration:none}
</style>
</head>
<body>
<div class="wrap">
<div class="hero">
<h1>Offers Marketplace</h1>
<p>Discover legitimate partner offers, services and earning opportunities.</p>
</div>
<div class="card">
<h2>Verified Offers</h2>
<p>Verified partner offers will appear here after admin review.</p>
<a class="btn" href="/">← Back to Home</a>
</div>
<div class="card">
<h3>Coming Soon</h3>
<p>Affiliate offers, partner services and earning opportunities will be added here.</p>
</div>
</div>
</body>
</html>""")

urlpatterns = [path("", marketplace, name="offers_marketplace")]
