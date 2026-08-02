from firebase.firebase_config import db
from firebase_admin import firestore


def create_policy(data):

    db.collection("policies").add({
        "name": data["name"],
        "type": data["type"],
        "value": data["value"],
        "priority": data["priority"],
        "enabled": True,
        "owner_uid": data["owner_uid"],
        "created_at": firestore.SERVER_TIMESTAMP
    })


def get_all_policies(owner_uid):

    docs = (
        db.collection("policies")
        .where(
            filter=firestore.FieldFilter(
                "owner_uid",
                "==",
                owner_uid
            )
        )
        .stream()
    )

    policies = []

    for doc in docs:
        policy = doc.to_dict()
        policy["id"] = doc.id
        policies.append(policy)

    return policies


def update_policy_status(policy_id, enabled):

    db.collection("policies").document(policy_id).update({
        "enabled": enabled
    })


def delete_policy(policy_id):

    db.collection("policies").document(policy_id).delete()