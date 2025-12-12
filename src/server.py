import sys
import os
import json
import uuid
from datetime import datetime, timezone

sys.path.insert(0, "recursive_backtracking")

from flask import Flask, request, jsonify, abort
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId

from maze import Maze
from json_maze import getJson

app = Flask(__name__)

# ===== 1. Configuration MongoDB =====
MONGO_URI = os.getenv("MONGODB_URI")

mazes_collection = None
scores_collection = None

if not MONGO_URI:
    print("ATTENTION: MONGODB_URI non trouvé. Mode sans base de données (mémoire seulement).")
else:
    try:
        # Connexion au cluster
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Récupération de la base par défaut (celle indiquée dans l'URI)
        db = client["pacman_db"]
        
        # Collection 'mazes'
        mazes_collection = db["mazes"]
        # Collection 'scores' pour le leaderboard
        scores_collection = db["scores"]
        
        # Index pour trier par date rapidement
        mazes_collection.create_index([("created_at", ASCENDING)])
        # Index pour le leaderboard : trier rapidement par score décroissant
        scores_collection.create_index([("score", DESCENDING)])
        print("Connexion MongoDB réussie !")
    except Exception as e:
        print(f"Erreur connexion MongoDB: {e}")
        mazes_collection = None

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "Maze API running", 
        "db_connected": mazes_collection is not None,
        "routes": ["/generate", "/mazes", "/maze/<id>", "/maze/<id>/rate"]
    }), 200

@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200

# ===== 2. Génération et Sauvegarde =====

@app.route("/generate", methods=["GET"])
def generate():
    # Récupération des paramètres
    width = int(request.args.get("width", 39))
    height = int(request.args.get("height", 19))
    nbcycle = int(request.args.get("nb_cycles", 10))
    nb_wrap_tunnels = int(request.args.get("num_tunnels_wrap", 2))
    nb_center_tunnels = int(request.args.get("num_tunnels_centre", 5))

    # Création du labyrinthe
    maze = Maze(width, height, nbcycle, nb_wrap_tunnels, nb_center_tunnels)
    maze.generate_maze()
    
    # Transformation en dictionnaire Python
    maze_json_str = getJson(maze)
    maze_data = json.loads(maze_json_str)

    # Sauvegarde en base de données
    if mazes_collection is not None:
        document = {
            "created_at": datetime.now(timezone.utc),
            "note": None,  # Pas de note à la création
            "params": {
                "width": width,
                "height": height,
                "nb_cycles": nbcycle
            },
            "data": maze_data # Stockage de la structure du labyrinthe
        }
        
        try:
            result = mazes_collection.insert_one(document)
            # On renvoie l'ID MongoDB au client
            maze_data["id"] = str(result.inserted_id)
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            maze_data["id"] = str(uuid.uuid4()) # Fallback ID temporaire
    else:
        # Mode hors ligne
        maze_data["id"] = str(uuid.uuid4())

    return jsonify(maze_data)




# ===== 3. Lecture d'un labyrinthe par ID =====
@app.route("/maze/<maze_id>", methods=["GET"])
def get_maze(maze_id):
    if mazes_collection is None:
        return abort(503, description="Database not connected")

    try:
        # Recherche par _id (ObjectId)
        doc = mazes_collection.find_one({"_id": ObjectId(maze_id)})
    except:
        return abort(400, description="Invalid Maze ID format")

    if not doc:
        return abort(404, description="Maze not found")
    
    # Reconstruction de la réponse 
    response_data = doc["data"]
    response_data["id"] = str(doc["_id"])
    
    # Ajout de la note si elle existe
    if "note" in doc:
        response_data["user_note"] = doc["note"]

    return jsonify(response_data), 200


# ===== 3b. Liste de tous les labyrinthes =====
@app.route("/mazes", methods=["GET"])
def list_mazes():

    if mazes_collection is None:
        return abort(503, description="Database not connected")

    limit = int(request.args.get("limit", 20))
    page = int(request.args.get("page", 1))
    skip = (page - 1) * limit

    cursor = mazes_collection.find({}, {"data": 0}).sort("_id", DESCENDING).skip(skip).limit(limit)

    mazes = []
    for doc in cursor:
        created = doc["created_at"]
        if hasattr(created, "isoformat"):
            created = created.isoformat()

        mazes.append({
            "id": str(doc["_id"]),
            "created_at": created,
            "params": doc["params"],
            "user_note": doc.get("note")
        })

    return jsonify({"count": len(mazes), "page": page, "mazes": mazes}), 200


# ===== 5. Scores / Leaderboard =====
@app.route("/score", methods=["POST"])
def post_score():
    """Receives a score submission and stores it in `scores` collection.
    Expected JSON body: { "player_name": "...", "score": 123, "maze_id": "..." (optional) }
    """
    if scores_collection is None:
        return abort(503, description="Database not connected")

    if not request.json:
        return abort(400, description="JSON body required")

    player_name = request.json.get("player_name")
    score = request.json.get("score")
    maze_id = request.json.get("maze_id")

    if not player_name or not isinstance(player_name, str) or len(player_name.strip()) == 0:
        return abort(400, description="player_name required")

    player_name = player_name.strip()
    if len(player_name) > 20:
        player_name = player_name[:20]

    try:
        score = int(score)
    except Exception:
        return abort(400, description="score must be an integer")

    doc = {
        "player_name": player_name,
        "score": score,
        "created_at": datetime.now(timezone.utc)
    }
    if maze_id:
        doc["maze_id"] = maze_id

    try:
        result = scores_collection.insert_one(doc)
        return jsonify({"status": "ok", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return abort(500, description=str(e))


@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    """Return top scores. Query params: limit (default 5), maze_id (optional).
    """
    if scores_collection is None:
        return abort(503, description="Database not connected")

    try:
        limit = int(request.args.get("limit", 5))
    except Exception:
        limit = 5

    maze_id = request.args.get("maze_id")
    query = {}
    if maze_id:
        query["maze_id"] = maze_id

    try:
        cursor = scores_collection.find(query).sort("score", DESCENDING).limit(limit)
    except Exception as e:
        return abort(500, description=str(e))

    results = []
    for doc in cursor:
        created = doc.get("created_at")
        if hasattr(created, "isoformat"):
            created = created.isoformat()

        results.append({
            "player_name": doc.get("player_name"),
            "score": doc.get("score"),
            "created_at": created,
            "maze_id": doc.get("maze_id")
        })

    return jsonify({"count": len(results), "leaderboard": results}), 200

# ===== 4. Notation d'un labyrinthe =====

@app.route("/maze/<maze_id>/rate", methods=["POST"])
def rate_maze(maze_id):

    if mazes_collection is None:
        return abort(503, description="Database not connected")

    # Validation de l'entrée
    if not request.json or 'note' not in request.json:
        return abort(400, description="JSON body with 'note' required")

    note_val = request.json.get('note')

    try:
        # If client explicitly sent null, set note to None in DB
        if note_val is None:
            result = mazes_collection.update_one(
                {"_id": ObjectId(maze_id)},
                {"$set": {"note": None}}
            )
            if result.matched_count == 0:
                return abort(404, description="Maze not found")
            return jsonify({"status": "success", "new_note": None}), 200

        # Otherwise expect an integer 0-10
        new_note = int(note_val)
        if not (0 <= new_note <= 10):
            return abort(400, description="Note must be between 0 and 10")

        result = mazes_collection.update_one(
            {"_id": ObjectId(maze_id)},
            {"$set": {"note": new_note}}
        )
        if result.matched_count == 0:
            return abort(404, description="Maze not found")

        return jsonify({"status": "success", "new_note": new_note}), 200

    except ValueError:
        return abort(400, description="Note must be an integer or null")
    except Exception as e:
        return abort(500, description=str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
