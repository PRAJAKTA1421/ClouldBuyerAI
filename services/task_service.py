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

    db.collection("tasks").document(task_id).update({

        "status": status

    })