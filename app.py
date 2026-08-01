import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, redirect, render_template, request, url_for


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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("auth.html", mode="login")


@app.route("/register")
def register():
    return render_template("auth.html", mode="register")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/agents")
def agents():
    return render_template("agents.html")


@app.route("/tasks")
def tasks():
    return render_template("tasks.html")


@app.route("/assign-task")
def assign_task():
    return render_template("assign_task.html")


@app.route("/wallets")
def wallets():
    return render_template("wallets.html")


@app.route("/transactions")
def transactions():
    return render_template("transactions.html")


@app.route("/security-policies")
def security_policies():
    return render_template("security_policies.html")


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


if __name__ == "__main__":
    app.run(debug=True)
