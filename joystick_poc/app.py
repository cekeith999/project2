#bodies file
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os, time

@app.route("/debug/radios")
def debug_radios():
    return render_template("debug_radios.html")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)


@app.route('/healthz')
def healthz():
    return 'ok', 200



# ---------------- Config ----------------
WEB_PORT = 5050

app = Flask(__name__, template_folder='templates', static_folder='static')

# --- QUESTION_BANK (Keep this as defined before) ---
QUESTION_BANK = [
    {
        "question": "Which weekend plan would I pick?",
        "options":  ["Beach day", "Mountain hike", "Movie marathon"]
    },
    {
        "question": "What's my biggest pet peeve?",
        "options":  ["Loud chewing", "Being late", "Leaving dishes"]
    },
    {
        "question": "If I could only eat one food for a year, what would it be?",
        "options":  ["Pizza", "Tacos", "Sushi"]
    }
]

# --- MODIFIED Game State ---
game_state = {
    "question_idx": None,        # Now starts as None, must be selected by P1
    "p1_selected": None,         # int or None
    "locked": False,
    "p2_guess": None,
    "result": None
}

# Helper functions remain the same
def get_current_question():
    if game_state["question_idx"] is None:
        return None
    idx = game_state["question_idx"] % len(QUESTION_BANK)
    return QUESTION_BANK[idx]

def reset_round():
    # Only reset the round-specific details, not the question index
    game_state["question_idx"] = None
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
    current_q = get_current_question()
    
    # Base state includes the full question list and the current index
    full_state = {
        "question_bank": QUESTION_BANK,  # Send the whole bank to the client
        "question_idx": game_state["question_idx"],
        "p1_selected": game_state["p1_selected"],
        "locked": game_state["locked"],
        "p2_guess": game_state["p2_guess"],
        "result": game_state["result"],
        # The specific question/options are added only if an index is set
        "question": current_q["question"] if current_q else "Please select a question.",
        "options": current_q["options"] if current_q else []
    }
    return jsonify(full_state)

# selecting the question
@app.route("/api/p1/set_question", methods=["POST"])
def api_p1_set_question():
    data = request.get_json(silent=True) or {}
    try:
        idx = int(data.get("idx"))
    except Exception:
        return jsonify({"ok": False, "error": "bad index"}), 400

    if idx < 0 or idx >= len(QUESTION_BANK):
        return jsonify({"ok": False, "error": "out of range"}), 400

    # If P1 selects a new question, reset the rest of the round data
    if game_state["question_idx"] != idx:
        reset_round() # This ensures P2 doesn't guess on a locked answer from a *different* question
        game_state["question_idx"] = idx

    return jsonify({"ok": True})

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
@app.route('/debug/radios')
def debug_radios():
    return render_template('debug_radios.html')
