from firebase.firebase_config import db


def get_dashboard_stats():

    total_agents = len(list(db.collection("agents").stream()))

    active_agents = len(
        list(
            db.collection("agents")
            .where("status", "==", "Active")
            .stream()
        )
    )

    wallet_balance = 0
    today_spend = 0
    risk_score = 0

    return {
        "agents": total_agents,
        "active_agents": active_agents,
        "wallet_balance": wallet_balance,
        "today_spend": today_spend,
        "risk_score": risk_score
    }