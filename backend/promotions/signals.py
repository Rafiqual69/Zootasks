from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import PromotionClaim

@receiver(post_save, sender=PromotionClaim)
def send_promotion_notification(sender, instance, created, **kwargs):
    if instance.status == "approved":
        subject = f"✅ প্রমোশন অনুমোদিত - {instance.promotion.title}"
        message = f"""
আপনার প্রমোশন জমা অনুমোদিত হয়েছে!

প্রমোশন: {instance.promotion.title}
পুরস্কার: ৳{instance.promotion.reward}

আপনার ড্যাশবোর্ডে আয় যুক্ত হয়েছে।

ZooTasks টিম
        """
        send_mail(subject, message, "noreply@zootasks.com", [instance.worker.email], fail_silently=True)
