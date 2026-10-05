import logging

from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import PromotionClaim

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=PromotionClaim)
def mark_promotion_approval_transition(sender, instance, **kwargs):
    instance._promotion_just_approved = False
    if not instance.pk or instance.status != "approved":
        return
    previous = sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    instance._promotion_just_approved = previous != "approved"


@receiver(post_save, sender=PromotionClaim)
def send_promotion_notification(sender, instance, created, **kwargs):
    just_approved = getattr(instance, "_promotion_just_approved", False)
    if not just_approved and not (created and instance.status == "approved"):
        return

    subject = f"✅ প্রমোশন অনুমোদিত - {instance.promotion.title}"
    message = f"""
আপনার প্রমোশন জমা অনুমোদিত হয়েছে!

প্রমোশন: {instance.promotion.title}
পুরস্কার: ৳{instance.promotion.reward}

আপনার ড্যাশবোর্ডে আয় যুক্ত হয়েছে।

ZooTasks টিম
        """

    def deliver():
        try:
            send_mail(subject, message, "noreply@zootasks.com", [instance.worker.email], fail_silently=True)
        except Exception:
            logger.exception("Promotion approval notification delivery failed")

    transaction.on_commit(deliver)
