from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import TaskClaim

@receiver(post_save, sender=TaskClaim)
def send_task_notification(sender, instance, created, **kwargs):
    if instance.status == "approved":
        subject = f"✅ টাস্ক অনুমোদিত - {instance.task.title}"
        message = f"""
আপনার টাস্ক জমা অনুমোদিত হয়েছে!

টাস্ক: {instance.task.title}
পুরস্কার: ৳{instance.task.reward}

আপনার ড্যাশবোর্ডে আয় যুক্ত হয়েছে।

ZooTasks টিম
        """
        send_mail(subject, message, "noreply@zootasks.com", [instance.worker.email], fail_silently=True)
