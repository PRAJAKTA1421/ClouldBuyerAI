from firebase_admin import firestore


def task_model(data):

    return {

        "title": data["title"],

        "description": data["description"],

        "agent_id": data["agent_id"],

        "agent_name": data["agent_name"],

        "wallet_id": data["wallet_id"],

        "wallet_name": data["wallet_name"],

        "priority": data["priority"],

        "status": "Pending",

        "owner_uid": data["owner_uid"],

        "created_at": firestore.SERVER_TIMESTAMP

    }