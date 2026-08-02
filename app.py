import json
import os
import random
import secrets   # add this at the top of app.py
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    session,
    flash
)
from datetime import datetime
from firebase.firebase_config import auth, db
from firebase_admin import auth as admin_auth, firestore
from firebase.firebase_config import auth
from services.dashboard_service import get_dashboard_stats
from services.agent_service import (
    create_agent,
    get_all_agents,
    delete_agent,
    update_agent_status
)
from services.wallet_service import (
    create_wallet,
    get_all_wallets,
    delete_wallet,
    update_wallet_status
)
from services.task_service import (
    create_task,
    get_all_tasks,
    delete_task,
    update_task_status,
    update_task_progress
)
from services.transaction_service import (
    create_transaction,
    get_all_transactions,
    update_transaction_status
)
from services.policy_services import (
    create_policy,
    get_all_policies,
    update_policy_status,
    delete_policy
)
app = Flask(__name__)


def load_local_env():
    """Load local development secrets without adding a dependency."""
    env_file = Path(app.root_path) / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()

# Secret key for Flask sessions
app.secret_key = os.getenv("SECRET_KEY", "CloudBuyerAI@2026")

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("auth.html", mode="login")

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        user = auth.sign_in_with_email_and_password(email, password)

        session["user"] = {
            "email": email,
            "idToken": user["idToken"],
            "localId": user["localId"]
        }

        return redirect(url_for("dashboard"))

    except Exception as e:
        import traceback

        traceback.print_exc()
        print("\n========== FIREBASE ERROR ==========")
        print(e)
        print("====================================\n")

        flash(str(e))

        return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("auth.html", mode="register")

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        # Create Firebase Authentication user
        user = admin_auth.create_user(
            email=email,
            password=password,
            display_name=username
        )

        # Save extra information in Firestore
        db.collection("users").document(user.uid).set({
            "uid": user.uid,
            "username": username,
            "email": email,
            "role": "owner",
            "createdAt": firestore.SERVER_TIMESTAMP
        })

        # Log in immediately
        firebase_user = auth.sign_in_with_email_and_password(email, password)

        session["user"] = {
            "email": email,
            "localId": firebase_user["localId"],
            "idToken": firebase_user["idToken"]
        }

        flash("Registration successful!")
        return redirect(url_for("dashboard"))

    except Exception as e:
        print(e)
        flash("Registration failed. Email may already exist.")
        return redirect(url_for("register"))

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    stats = get_dashboard_stats()

    user = {
        "username": session["user"]["email"].split("@")[0],
        "role": "Owner"
    }

    return render_template(
         "dashboard.html",
         stats=stats,
         user=user
    )

@app.route("/agents", methods=["GET", "POST"])
def agents():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        data = {
            "name": request.form.get("name"),
            "type": request.form.get("type"),
            "purpose": request.form.get("purpose"),
            "description": request.form.get("description"),
            "wallet": request.form.get("wallet"),
            "model": request.form.get("model"),
            "owner_uid": session["user"]["localId"]
        }

        try:

            create_agent(data)

            flash("Agent created successfully!")

        except Exception as e:

            flash(str(e))


        return redirect(url_for("agents"))
    agents = get_all_agents(session["user"]["localId"])
    wallets = get_all_wallets(session["user"]["localId"])

    return render_template(
        "agents.html",
        agents=agents,
        wallets=wallets
    )

@app.route("/delete-agent/<agent_id>")
def delete_agent_route(agent_id):

    if "user" not in session:
        return redirect(url_for("login"))

    delete_agent(agent_id)

    flash("Agent deleted!")

    return redirect(url_for("agents"))

@app.route("/freeze-agent/<agent_id>")
def freeze_agent(agent_id):

    update_agent_status(agent_id, "Frozen")

    flash("Agent frozen.")

    return redirect(url_for("agents"))

@app.route("/activate-agent/<agent_id>")
def activate_agent(agent_id):

    update_agent_status(agent_id, "Active")

    flash("Agent activated.")

    return redirect(url_for("agents"))

@app.route("/tasks")
def tasks():

    if "user" not in session:
        return redirect(url_for("login"))

    tasks = get_all_tasks(
        session["user"]["localId"]
    )

    agents = get_all_agents(
        session["user"]["localId"]
    )

    return render_template(
        "tasks.html",
        tasks=tasks,
        agents=agents
    )

@app.route("/create-task", methods=["POST"])
def create_task_route():

    if "user" not in session:
        return redirect(url_for("login"))

    agent_id = request.form.get("agent")

    agents = get_all_agents(
        session["user"]["localId"]
    )

    selected_agent = None

    for agent in agents:

        if agent["id"] == agent_id:
            selected_agent = agent
            break

    if selected_agent is None:

        flash("Invalid agent selected.")

        return redirect(url_for("tasks"))

    data = {

        "title": request.form.get("title"),

        "description": request.form.get("description"),

        "priority": request.form.get("priority"),

        "agent_id": selected_agent["id"],

        "agent_name": selected_agent["name"],

        "wallet_name": selected_agent["wallet_name"],

        "owner_uid": session["user"]["localId"]

    }

    create_task(data)

    flash("Task created successfully!")

    return redirect(url_for("tasks"))

@app.route("/start-task/<task_id>")
def start_task(task_id):

    if "user" not in session:
        return redirect(url_for("login"))

    db.collection("tasks").document(task_id).update({
        "status": "Running",
        "progress": 10,
        "started_at": firestore.SERVER_TIMESTAMP
    })

    flash("Task started successfully!")

    return redirect(url_for("tasks"))

@app.route("/pause-task/<task_id>")
def pause_task(task_id):

    if "user" not in session:
        return redirect(url_for("login"))

    update_task_status(task_id, "Paused")

    flash("Task paused.")

    return redirect(url_for("tasks"))

@app.route("/resume-task/<task_id>")
def resume_task(task_id):

    if "user" not in session:
        return redirect(url_for("login"))

    update_task_status(task_id, "Running")

    flash("Task resumed.")

    return redirect(url_for("tasks"))

@app.route("/complete-task/<task_id>")
def complete_task(task_id):

    if "user" not in session:
        return redirect(url_for("login"))

    task_ref = db.collection("tasks").document(task_id)
    task = task_ref.get().to_dict()

    execution_time = 0

    if task.get("started_at"):

        execution_time = (
            datetime.utcnow() -
            task["started_at"].replace(tzinfo=None)
        ).total_seconds()

    task_ref.update({
        "status": "Completed",
        "progress": 100,
        "completed_at": firestore.SERVER_TIMESTAMP,
        "execution_time": round(execution_time, 2)
    })

    flash("Task completed!")

    return redirect(url_for("tasks"))

@app.route("/fail-task/<task_id>")
def fail_task(task_id):

    if "user" not in session:
        return redirect(url_for("login"))

    update_task_status(task_id, "Failed")

    flash("Task failed.")

    return redirect(url_for("tasks"))

@app.route("/delete-task/<task_id>")
def delete_task_route(task_id):

    if "user" not in session:
        return redirect(url_for("login"))

    delete_task(task_id)

    flash("Task deleted.")

    return redirect(url_for("tasks"))

@app.route("/task-progress/<task_id>")
def task_progress(task_id):

    doc = db.collection("tasks").document(task_id).get()

    if not doc.exists:
        return jsonify({"error": "Task not found"}), 404

    task = doc.to_dict()

    progress = task.get("progress", 0)
    status = task.get("status", "Pending")
    execution_time = task.get("execution_time", 0)

    # Increase progress only while task is running
    if status == "Running":

        progress += random.randint(2, 6)
        execution_time += 2     # because frontend polls every 2 seconds

        if progress >= 100:
            progress = 100
            status = "Completed"

        db.collection("tasks").document(task_id).update({
            "progress": progress,
            "status": status,
            "execution_time": execution_time
        })

    return jsonify({
        "id": doc.id,
        "progress": progress,
        "status": status,
        "execution_time": execution_time
    })

@app.route("/assign-task")
def assign_task():
    return render_template("assign_task.html")


@app.route("/wallets", methods=["GET", "POST"])
def wallets():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        wallet_address = "0x" + secrets.token_hex(20)

        data = {
            "wallet_name": request.form.get("wallet_name"),
            "wallet_address": wallet_address,
            "network": request.form.get("network"),
            "balance": float(request.form.get("balance")),
            "daily_limit": float(request.form.get("daily_limit")),
            "owner_uid": session["user"]["localId"]
        }

        create_wallet(data)

        flash("Wallet added successfully!")

        return redirect(url_for("wallets"))

    wallets = get_all_wallets(session["user"]["localId"])

    return render_template(
        "wallets.html",
        wallets=wallets
    )

@app.route("/delete-wallet/<wallet_id>")
def delete_wallet_route(wallet_id):

    delete_wallet(wallet_id)

    return redirect(url_for("wallets"))


@app.route("/freeze-wallet/<wallet_id>")
def freeze_wallet(wallet_id):

    update_wallet_status(wallet_id, "Frozen")

    return redirect(url_for("wallets"))


@app.route("/activate-wallet/<wallet_id>")
def activate_wallet(wallet_id):

    update_wallet_status(wallet_id, "Active")

    return redirect(url_for("wallets"))

@app.route("/transactions")
def transactions():

    if "user" not in session:
        return redirect(url_for("login"))

    transactions = get_all_transactions(
        session["user"]["localId"]
    )

    wallets = get_all_wallets(
        session["user"]["localId"]
    )

    return render_template(
        "transactions.html",
        transactions=transactions,
        wallets=wallets
    )

@app.route("/create-transaction", methods=["POST"])
def create_transaction_route():

    if "user" not in session:
        return redirect(url_for("login"))


    wallet_name = request.form.get("wallet")


    # Get available wallets from Firebase
    wallets = get_all_wallets(
        session["user"]["localId"]
    )


    selected_wallet = None


    # Find selected wallet
    for wallet in wallets:

        if wallet["wallet_name"] == wallet_name:
            selected_wallet = wallet
            break


    # Wallet validation
    if selected_wallet is None:

        flash("Invalid wallet selected.")

        return redirect(url_for("transactions"))



    data = {

        "merchant": request.form.get("merchant"),

        "wallet": selected_wallet["wallet_name"],

        "wallet_address": selected_wallet["wallet_address"],

        "network": selected_wallet["network"],

        "amount": float(request.form.get("amount")),

        "purpose": request.form.get("purpose"),

        "owner_uid": session["user"]["localId"]

    }


    create_transaction(data)


    flash("Transaction created successfully!")


    return redirect(url_for("transactions"))

@app.route("/approve-transaction/<transaction_id>")
def approve_transaction(transaction_id):

    update_transaction_status(transaction_id, "Approved")

    flash("Transaction approved!")

    return redirect(url_for("transactions"))

@app.route("/reject-transaction/<transaction_id>")
def reject_transaction(transaction_id):

    update_transaction_status(transaction_id, "Rejected")

    flash("Transaction rejected!")

    return redirect(url_for("transactions"))

@app.route("/security-policies")
def security_policies():

    if "user" not in session:
        return redirect(url_for("login"))

    policies = get_all_policies(
        session["user"]["localId"]
    )

    return render_template(
        "security_policies.html",
        policies=policies
    )

@app.route("/create-policy", methods=["POST"])
def create_policy_route():

    if "user" not in session:
        return redirect(url_for("login"))

    data = {

        "name": request.form.get("name"),
        "type": request.form.get("type"),
        "value": request.form.get("value"),
        "priority": request.form.get("priority"),
        "owner_uid": session["user"]["localId"]

    }

    create_policy(data)

    flash("Policy created successfully!")

    return redirect(url_for("security_policies"))

@app.route("/enable-policy/<policy_id>")
def enable_policy(policy_id):

    update_policy_status(policy_id, True)

    return redirect(url_for("security_policies"))


@app.route("/disable-policy/<policy_id>")
def disable_policy(policy_id):

    update_policy_status(policy_id, False)

    return redirect(url_for("security_policies"))


@app.route("/delete-policy/<policy_id>")
def delete_policy_route(policy_id):

    delete_policy(policy_id)

    return redirect(url_for("security_policies"))

@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/alerts")
def alerts():
    return render_template("alerts.html")


@app.get("/auth/google")
def google_login():
    load_local_env()
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if not client_id:
        return redirect(url_for("login", error="google_not_configured"))
    query = urlencode({
        "client_id": client_id,
        "redirect_uri": url_for("google_callback", _external=True),
        "response_type": "code",
        "scope": "openid email profile",
        "prompt": "select_account",
    })
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")


@app.get("/auth/google/callback")
def google_callback():
    # The authorization code must be exchanged with a Google client secret.
    # Until credentials are configured, return users to the sign-in screen.
    return redirect(url_for("login"))


@app.post("/api/chat")
def chat():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return jsonify(error="MISTRAL_API_KEY is not configured on the server."), 503

    messages = request.get_json(silent=True, force=False) or []
    if not isinstance(messages, list):
        return jsonify(error="Invalid chat request."), 400

    safe_messages = [
        {"role": item.get("role"), "content": item.get("content", "")[:2000]}
        for item in messages[-12:]
        if isinstance(item, dict) and item.get("role") in {"user", "assistant"}
        and isinstance(item.get("content", ""), str)
    ]
    if not safe_messages:
        return jsonify(error="Please enter a message."), 400

    payload = json.dumps({
        "model": "mistral-small-latest",
        "messages": [{"role": "system", "content": "You are Kill Switch Assistant, a concise security dashboard helper."}] + safe_messages,
        "max_tokens": 400,
    }).encode("utf-8")
    api_request = Request(
        "https://api.mistral.ai/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(api_request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return jsonify(reply=data["choices"][0]["message"]["content"])
    except (HTTPError, URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return jsonify(error="The assistant is temporarily unavailable. Please try again."), 502


@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully")

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)