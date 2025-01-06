# tasks/urls.py
from django.urls import path
from .views import create_task, delete_task

urlpatterns = [
    path("tasks/create/", create_task, name="create-task"),
    path("tasks/<str:task_id>/delete/", delete_task, name="delete-task"),
]
