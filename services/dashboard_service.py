from firebase.firebase_config import db


def get_dashboard_stats():

    # ----------------------------
    # Agents
    # ----------------------------
    agents = list(db.collection("agents").stream())

    total_agents = len(agents)

    active_agents = 0

    for agent in agents:
        data = agent.to_dict()

        if data.get("status") == "Active":
            active_agents += 1

    # ----------------------------
    # Wallet Balance
    # ----------------------------
    wallets = list(db.collection("wallets").stream())

    wallet_balance = 0

    for wallet in wallets:

        wallet_balance += float(
            wallet.to_dict().get("balance", 0)
        )

    # ----------------------------
    # Transactions
    # ----------------------------
    transactions = list(
        db.collection("transactions").stream()
    )

    today_spend = 0

    blocked = 0

    for tx in transactions:

        data = tx.to_dict()

        amount = float(
            data.get("amount", 0)
        )

        today_spend += amount

        if data.get("status") == "Blocked":
            blocked += 1

    # ----------------------------
    # Risk Score
    # ----------------------------

    if len(transactions) == 0:

        risk_score = 0

    else:

        risk_score = round(
            (blocked / len(transactions)) * 100
        )

    return {

        "agents": total_agents,

        "active_agents": active_agents,

        "wallet_balance": wallet_balance,

        "today_spend": today_spend,

        "risk_score": risk_score

    }