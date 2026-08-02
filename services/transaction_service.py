from firebase.firebase_config import db
from firebase_admin import firestore
import random
import string

from services.policy_engine import evaluate_transaction
def random_hash():
    return "0x" + "".join(random.choices("abcdef0123456789", k=64))


def create_transaction(data):

    decision = evaluate_transaction(
        data["owner_uid"],
        float(data["amount"])
    )

    tx = {

        "merchant": data["merchant"],

        "wallet": data["wallet"],

        "wallet_address": data["wallet_address"],

        "amount": data["amount"],

        "purpose": data["purpose"],

        "status": decision["status"],

        "reason": decision["reason"],

        "network": data["network"],

        "gas_fee": round(random.uniform(0.0001, 0.003), 6),

        "tx_hash": random_hash(),

        "owner_uid": data["owner_uid"],

        "created_at": firestore.SERVER_TIMESTAMP

    }

    db.collection("transactions").add(tx)

def get_all_transactions(owner_uid):

    docs = (
        db.collection("transactions")
        .where(filter=firestore.FieldFilter("owner_uid", "==", owner_uid))
        .stream()
    )

    transactions = []

    for doc in docs:
        t = doc.to_dict()
        t["id"] = doc.id
        transactions.append(t)

    return transactions

def update_transaction_status(transaction_id, status):

    db.collection("transactions").document(transaction_id).update({
        "status": status
    })