from django.db import models


class Offer(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("paused", "Paused"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    partner_name = models.CharField(max_length=150)
    reward = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
