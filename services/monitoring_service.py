import psutil
from datetime import datetime

from firebase.firebase_config import db
from firebase_admin import firestore


def get_cpu_usage():

    return psutil.cpu_percent(interval=1)



def get_memory_usage():

    memory = psutil.virtual_memory()

    return memory.percent



def get_network_status():

    return {
        "status": "Online",
        "latency": "12 ms"
    }



def get_live_transactions():

    docs = (
        db.collection("transactions")
        .order_by(
            "created_at",
            direction=firestore.Query.DESCENDING
        )
        .limit(5)
        .stream()
    )


    transactions=[]


    for doc in docs:

        tx = doc.to_dict()

        transactions.append({

            "merchant": tx.get("merchant"),

            "amount": tx.get("amount"),

            "status": tx.get("status")

        })


    return transactions



def get_wallet_activity():

    wallets = (
        db.collection("wallets")
        .limit(5)
        .stream()
    )


    data=[]


    for wallet in wallets:

        w = wallet.to_dict()

        data.append({

            "wallet":
            w.get("wallet_name"),

            "status":
            w.get("status","Active")

        })


    return data



def get_monitoring_data():

    return {

        "cpu":
        get_cpu_usage(),


        "memory":
        get_memory_usage(),


        "network":
        get_network_status(),


        "transactions":
        get_live_transactions(),


        "wallets":
        get_wallet_activity(),


        "time":
        datetime.now().strftime(
            "%H:%M:%S"
        )

    }