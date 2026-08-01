from firebase.firebase_config import db
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


def create_wallet(data):

    db.collection("wallets").add({
        "wallet_name": data["wallet_name"],
        "wallet_address": data["wallet_address"],
        "network": data["network"],
        "balance": data["balance"],
        "status": "Active",
        "daily_limit": data["daily_limit"],
        "owner_uid": data["owner_uid"],
        "created_at": firestore.SERVER_TIMESTAMP
    })


def get_all_wallets(owner_uid):

    wallets = []

    docs = (
        db.collection("wallets")
        .where(filter=FieldFilter("owner_uid", "==", owner_uid))
        .stream()
    )

    for doc in docs:

        wallet = doc.to_dict()

        wallet["id"] = doc.id


        # Count assigned agents
        agent_docs = db.collection("agents").where(
            filter=FieldFilter(
                "wallet_id",
                "==",
                doc.id
            )
        ).stream()


        wallet["agent_count"] = len(list(agent_docs))


        wallets.append(wallet)


    return wallets


def delete_wallet(wallet_id):
    db.collection("wallets").document(wallet_id).delete()


def update_wallet_status(wallet_id, status):

    db.collection("wallets").document(wallet_id).update({
        "status": status
    })