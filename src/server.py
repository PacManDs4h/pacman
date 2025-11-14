import sys

sys.path.insert(0, "recursive_backtracking")
from pymongo import MongoClient, ASCENDING
from flask import Flask, request, jsonify, abort
from datetime import datetime, timezone
import json
import uuid
import os
from maze import Maze
from json_maze import getJson   # retourne une string JSON (cf. ton fichier)


# --- accès à ton code existant ---
# (Dockerfile copie tout sous /app ; ici server.py est dans /app ;
#  le dossier /app/recursive_backtracking est donc au même niveau)

app = Flask(__name__)

# # ===== MongoDB Atlas =====
# MONGO_URI = os.getenv("MONGODB_URI")
# if not MONGO_URI:
#     raise RuntimeError("MONGODB_URI manquant (Render → Environment)")

# mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
# db = mongo.get_default_database()        # DB prise depuis l’URI
# mazes = db["mazes"]
# mazes.create_index([("created_at", ASCENDING)])


# def now_iso():
#     return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

# ===== Routes “utiles” =====


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Maze API running", "routes": ["/generate", "/maze/<id>", "/healthz"]}), 200


@app.route("/healthz", methods=["GET"])
def healthz():
    try:
        # mongo.admin.command("ping")
        return "ok", 200
    except Exception as e:
        return ("mongo error: " + str(e), 500)

# ===== Génération + stockage =====


@app.route("/generate", methods=["GET"])
def generate():
    # paramètres par défaut
    width = int(request.args.get("width", 39))
    height = int(request.args.get("height", 19))
    nbcycle = int(request.args.get("nb_cycles", 10))
    nb_wrap_tunnels = int(request.args.get("num_tunnels_wrap", 2))
    nb_center_tunnels = int(request.args.get("num_tunnels_centre", 5))

    maze = Maze(width, height, nbcycle, nb_wrap_tunnels, nb_center_tunnels)
    maze.generate_maze()

    return getJson(maze)

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
