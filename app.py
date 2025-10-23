from flask import Flask, render_template, request, jsonify, redirect, url_for
import os, time

# ---------------- Config ----------------
WEB_PORT = 5050

app = Flask(__name__, template_folder='templates', static_folder='static')

# ---------------- Minimal Game State ----------------
game_state = {
    "question": "Which weekend plan would I pick?",
    "options":  ["Beach day", "Mountain hike", "Movie marathon"],
    "p1_selected": None,     # int or None
    "locked": False,         # True once P1 locks
    "p2_guess": None,        # int or None
    "result": None           # None | "correct" | "wrong"
}

def reset_round():
    game_state["p1_selected"] = None
    game_state["locked"] = False
    game_state["p2_guess"] = None
    game_state["result"] = None

# ---------------- Pages ----------------
@app.route("/")
def home():
    # simple player chooser
    return render_template("index.html")

@app.route("/player/1")
def player1():
    return render_template("player1.html")

@app.route("/player/2")
def player2():
    return render_template("player2.html")

# ---------------- APIs ----------------
@app.route("/state")
def state():
    return jsonify(game_state)

# Player 1 actions
@app.route("/api/p1/select", methods=["POST"])
def api_p1_select():
    if game_state["locked"]:
        return jsonify({"ok": False, "error": "locked"}), 400
    data = request.get_json(silent=True) or {}
    try:
        idx = int(data.get("idx"))
    except Exception:
        return jsonify({"ok": False, "error": "bad index"}), 400
    if idx < 0 or idx >= len(game_state["options"]):
        return jsonify({"ok": False, "error": "out of range"}), 400
    game_state["p1_selected"] = idx
    return jsonify({"ok": True})

@app.route("/api/p1/lock", methods=["POST"])
def api_p1_lock():
    if game_state["p1_selected"] is None:
        return jsonify({"ok": False, "error": "no selection"}), 400
    game_state["locked"] = True
    return jsonify({"ok": True})

# Player 2 actions
@app.route("/api/p2/guess", methods=["POST"])
def api_p2_guess():
    if not game_state["locked"]:
        return jsonify({"ok": False, "error": "p1_not_locked"}), 400
    data = request.get_json(silent=True) or {}
    try:
        idx = int(data.get("idx"))
    except Exception:
        return jsonify({"ok": False, "error": "bad index"}), 400
    if idx < 0 or idx >= len(game_state["options"]):
        return jsonify({"ok": False, "error": "out of range"}), 400

    game_state["p2_guess"] = idx
    game_state["result"] = "correct" if idx == game_state["p1_selected"] else "wrong"
    return jsonify({"ok": True, "result": game_state["result"]})

@app.route("/api/reset", methods=["POST"])
def api_reset():
    reset_round()
    return jsonify({"ok": True})

# ---------------- Main ----------------
if __name__ == "__main__":
    print("TEMPLATES:", os.path.abspath(app.template_folder))
    print("STATIC   :", os.path.abspath(app.static_folder))
    app.run(debug=True, port=WEB_PORT)
