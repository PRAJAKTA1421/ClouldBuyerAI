from firebase.firebase_config import db
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


def create_agent(data):

    # Find selected wallet
    wallet_docs = db.collection("wallets").where(
        filter=FieldFilter(
            "wallet_address",
            "==",
            data["wallet"]
        )
    ).stream()

    wallet = None

    for doc in wallet_docs:
        wallet = doc.to_dict()
        wallet["id"] = doc.id

    if wallet is None:
        raise Exception("Wallet not found.")

    # Check if wallet already assigned
    existing = db.collection("agents").where(
        filter=FieldFilter(
            "wallet_id",
            "==",
            wallet["id"]
        )
    ).stream()

    if any(existing):
        raise Exception("Wallet already assigned to another agent.")

    # Save agent
    db.collection("agents").add({

        "name": data["name"],
        "type": data["type"],
        "purpose": data["purpose"],
        "description": data["description"],

        "wallet": wallet["wallet_address"],
        "wallet_name": wallet["wallet_name"],
        "wallet_id": wallet["id"],
        "network": wallet["network"],

        "model": data["model"],

        "status": "Active",
        "risk_score": 0,
        "daily_limit": 10000,

        "owner_uid": data["owner_uid"],

        "created_at": firestore.SERVER_TIMESTAMP
    })


def get_all_agents(owner_uid):
    agents = []

    docs = db.collection("agents").where(
        "owner_uid", "==", owner_uid
    ).stream()

    for doc in docs:
        agent = doc.to_dict()
        agent["id"] = doc.id
        agents.append(agent)

    return agents


def delete_agent(agent_id):
    db.collection("agents").document(agent_id).delete()


def update_agent_status(agent_id, status):
    db.collection("agents").document(agent_id).update({
        "status": status
    })
