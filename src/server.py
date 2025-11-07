import sys

sys.path.insert(0, "recursive_backtracking")

from json_maze import getJson   # retourne une string JSON (cf. ton fichier)
from maze import Maze
import os
import uuid
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify, abort
from pymongo import MongoClient, ASCENDING

# --- accès à ton code existant ---
# (Dockerfile copie tout sous /app ; ici server.py est dans /app ;
#  le dossier /app/recursive_backtracking est donc au même niveau)

app = Flask(__name__)

# ===== MongoDB Atlas =====
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError("MONGODB_URI manquant (Render → Environment)")

mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = mongo.get_default_database()        # DB prise depuis l’URI
mazes = db["mazes"]
mazes.create_index([("created_at", ASCENDING)])


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

# ===== Routes “utiles” =====


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Maze API running", "routes": ["/generate", "/maze/<id>", "/healthz"]}), 200


@app.route("/healthz", methods=["GET"])
def healthz():
    try:
        mongo.admin.command("ping")
        return "ok", 200
    except Exception as e:
        return ("mongo error: " + str(e), 500)

# ===== Génération + stockage =====


@app.route("/generate", methods=["GET"])
def generate():
    # Lis les paramètres (avec tes valeurs par défaut actuelles)
    width = int(request.args.get("width",  39))
    height = int(request.args.get("height", 19))
    # tes 3 paramètres spécifiques au constructeur Maze
    nb_cycles = int(request.args.get("cycles",        10))
    nb_wrap_tunnels = int(request.args.get("wrap_tunnels",   2))
    nb_center_tunnels = int(request.args.get("center_tunnels", 5))
    seed = request.args.get("seed")  # optionnel

    # Génère le labyrinthe via ton code
    mz = Maze(width, height, nb_cycles, nb_wrap_tunnels, nb_center_tunnels)
    # ta méthode accepte un seed optionnel selon ton implémentation
    # (dans ton fichier, generate_maze(seed=None) existe)
    mz.generate_maze(seed=seed)

    # Récupère le JSON produit par ton code
    raw = getJson(mz)  # string JSON selon ton json_maze.py
    try:
        data = json.loads(raw)
    except Exception:
        # si jamais raw n’était pas un JSON valide (peu probable), on stocke brut
        data = {"raw": raw}

    # Document à stocker
    maze_id = str(uuid.uuid4())
    doc = {
        "_id": maze_id,
        "created_at": now_iso(),
        "params": {
            "width": width, "height": height,
            "cycles": nb_cycles,
            "wrap_tunnels": nb_wrap_tunnels,
            "center_tunnels": nb_center_tunnels,
            "seed": seed
        },
        # on stocke exactement ce que ton getJson produit (avec stats + "maze")
        "data": data
    }

    mazes.insert_one(doc)

    # Réponse client : id + même payload utile
    return jsonify({
        "id": maze_id,
        "created_at": doc["created_at"],
        "params": doc["params"],
        "data": data
    }), 200

# ===== Lecture par ID =====


@app.route("/maze/<maze_id>", methods=["GET"])
def get_maze(maze_id):
    doc = mazes.find_one({"_id": maze_id})
    if not doc:
        abort(404, description="Maze not found")
    # renvoyer avec une clé 'id' pour le client
    doc["id"] = doc.pop("_id")
    return jsonify(doc), 200


if __name__ == "__main__":
    # OK pour Render, sinon préfère gunicorn en prod
    app.run(host="0.0.0.0", port=8080)
