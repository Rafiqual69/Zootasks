from django.urls import path
from .views import marketplace, task_detail, claim_task, submit_task

urlpatterns = [
    path("", marketplace, name="task_marketplace"),
    path("<int:task_id>/", task_detail, name="task_detail"),
    path("<int:task_id>/claim/", claim_task, name="claim_task"),
    path("<int:task_id>/submit/", submit_task, name="submit_task"),
]
