# tasks/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import assign_staff_to_projects_90_100
from django.conf import settings
from pymongo import MongoClient

def get_db():
    client = MongoClient(settings.MONGO_URI)
    return client["your_database_name"]

@api_view(["POST"])
def create_task(request):
    """
    Create a new task in Mongo, then run assignment.
    """
    db = get_db()
    data = request.data

    new_task = {
        "title": data.get("title"),
        "requiredLOE": data.get("requiredLOE", 0),
        "assignedTo": None
    }
    result = db.tasks.insert_one(new_task)

    # After insertion, run assignment
    assign_staff_to_projects_90_100()

    return Response({"detail": "Task created and assignment triggered."}, status=201)

@api_view(["DELETE"])
def delete_task(request, task_id):
    """
    Delete an existing task in Mongo, then re-run assignment.
    """
    db = get_db()
    db.tasks.delete_one({"_id": task_id})

    # Re-run assignment
    assign_staff_to_projects_90_100()

    return Response({"detail": "Task deleted, re-assigned."}, status=200)
