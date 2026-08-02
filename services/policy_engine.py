from firebase.firebase_config import db
from firebase_admin import firestore


def evaluate_transaction(owner_uid, amount):

    print("CURRENT USER UID:", owner_uid)

    policies = (
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

    decision = {
        "status": "Approved",
        "reason": "Passed all policies"
    }


    for doc in policies:

        policy = doc.to_dict()

        print("POLICY FOUND:", policy)


        if not policy.get("enabled"):
            continue


        ptype = policy.get("type")

        value = policy.get("value")


        # -------------------------
        # Spending Limit
        # -------------------------

        if ptype == "Daily Spending Limit":

            limit = float(value)


            if amount > limit:

                return {

                    "status": "Blocked",

                    "reason":
                    f"Amount exceeds spending limit ₹{limit}"

                }



        # -------------------------
        # Transaction Limit
        # -------------------------

        if ptype == "Transaction Limit":

            limit = float(value)


            if amount > limit:

                return {

                    "status": "Blocked",

                    "reason":
                    f"Transaction exceeds limit ₹{limit}"

                }



        # -------------------------
        # Human Approval
        # -------------------------

        if ptype == "Human Approval":

            decision["status"] = "Pending Approval"

            decision["reason"] = (
                "Waiting for owner approval"
            )


    return decision