# tasks/services.py
from bson.objectid import ObjectId
from django.conf import settings
from pymongo import MongoClient

# Example: If you have a central Mongo connection in settings or elsewhere:
# MONGO_URI = settings.MONGO_URI
# client = MongoClient(MONGO_URI)
# db = client["your_database_name"]

def get_db():
    """
    Returns a reference to your MongoDB database.
    You could also do this once at module level if you prefer.
    """
    client = MongoClient(settings.MONGO_URI)
    return client["your_database_name"]

def assign_staff_to_projects_90_100():
    """
    Example 'matching' or 'assignment' function.
    1. Fetch all staff
    2. Fetch all unassigned or relevant projects/tasks
    3. Distribute tasks so each staff's LOE is between 90-100%
    4. Update records in Mongo
    """
    db = get_db()

    # 1. Fetch staff
    staff_cursor = db.staff.find({})
    staff_list = list(staff_cursor)

    # 2. Fetch tasks
    tasks_cursor = db.tasks.find({"assignedTo": None})  # or {"status": "New"}
    task_list = list(tasks_cursor)

    # (Pseudocode) Implement your custom logic:
    # e.g., Sort tasks by required LOE descending
    task_list.sort(key=lambda t: t["requiredLOE"], reverse=True)

    # Build a map of staff_id -> used_capacity
    staff_capacity_map = {}
    for s in staff_list:
        staff_capacity_map[s["_id"]] = {
            "capacity": s["capacity"],         # total capacity
            "currentLOE": s.get("currentLOE", 0)  # maybe store sum of assigned tasks
        }

    # 3. Assign tasks greedily (simple example)
    for task in task_list:
        best_fit_staff_id = None
        best_fit_remaining = None

        for st_id, info in staff_capacity_map.items():
            capacity = info["capacity"]
            current_loe = info["currentLOE"]
            task_loe = task["requiredLOE"]

            if current_loe + task_loe <= capacity:
                # This staff can take the task
                remaining = capacity - (current_loe + task_loe)

                # We look for the smallest leftover so we're close to 100%
                if best_fit_remaining is None or remaining < best_fit_remaining:
                    best_fit_remaining = remaining
                    best_fit_staff_id = st_id

        # If we found a staff who can fit this task
        if best_fit_staff_id:
            # Update DB
            db.tasks.update_one(
                {"_id": task["_id"]},
                {"$set": {"assignedTo": best_fit_staff_id}}
            )
            # Update staff capacity usage
            staff_capacity_map[best_fit_staff_id]["currentLOE"] += task["requiredLOE"]

    # Optionally, do a second pass to ensure no one is below 90%, etc.
    # Or skip if a single pass is enough.

    return "Assignment complete."
