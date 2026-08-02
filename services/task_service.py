from datetime import datetime

from firebase.firebase_config import db
from firebase_admin import firestore

def create_task(data):

    db.collection("tasks").add({

        "title": data["title"],
        "description": data["description"],

        "agent_id": data["agent_id"],
        "agent_name": data["agent_name"],

        "wallet_name": data["wallet_name"],

        "priority": data["priority"],

        "status": "Pending",

        "progress": 0,

        "started_at": None,

        "completed_at": None,

        "execution_time": 0,

        "owner_uid": data["owner_uid"],

        "created_at": firestore.SERVER_TIMESTAMP

    })

def get_all_tasks(owner_uid):

    tasks = []

    docs = db.collection("tasks") \
        .where("owner_uid", "==", owner_uid) \
        .stream()

    for doc in docs:

        task = doc.to_dict()
        task["id"] = doc.id

        tasks.append(task)

    return tasks


def delete_task(task_id):

    db.collection("tasks").document(task_id).delete()


def update_task_status(task_id, status):

    update_data = {
        "status": status
    }

    if status == "Running":

        update_data["started_at"] = datetime.utcnow()

    elif status == "Completed":

        update_data["completed_at"] = datetime.utcnow()

        update_data["execution_time"] = "2 min"

        update_data["progress"] = 100

    db.collection("tasks").document(task_id).update(update_data)


def update_task_progress(task_id, progress):

    db.collection("tasks").document(task_id).update({

        "progress": progress,

        "execution_time": firestore.Increment(1)

    })