import sys
import os
import json
import uuid
from datetime import datetime, timezone

# Ajout du chemin pour les modules internes
sys.path.insert(0, "recursive_backtracking")

from flask import Flask, request, jsonify, abort
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId

from maze import Maze
from json_maze import getJson

app = Flask(__name__)

# ===== 1. Configuration MongoDB =====
# On récupère l'URI depuis les variables d'environnement (Render ou Docker)
MONGO_URI = os.getenv("MONGODB_URI")

mazes_collection = None

if not MONGO_URI:
    print("ATTENTION: MONGODB_URI non trouvé. Mode sans base de données (mémoire seulement).")
else:
    try:
        # Connexion au cluster
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Récupération de la base par défaut (celle indiquée dans l'URI)
        db = client.get_default_database()
        
        # Collection 'mazes'
        mazes_collection = db["mazes"]
        
        # Index pour trier par date rapidement
        mazes_collection.create_index([("created_at", ASCENDING)])
        print("Connexion MongoDB réussie !")
    except Exception as e:
        print(f"Erreur connexion MongoDB: {e}")
        mazes_collection = None

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "Maze API running", 
        "db_connected": mazes_collection is not None,
        "routes": ["/generate", "/maze/<id>", "/maze/<id>/rate"]
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

# ===== 4. Notation d'un labyrinthe =====

@app.route("/maze/<maze_id>/rate", methods=["POST"])
def rate_maze(maze_id):
    """
    Attend un JSON : {"note": 5}
    Met à jour le champ 'note' du document en base.
    """
    if mazes_collection is None:
        return abort(503, description="Database not connected")

    # Validation de l'entrée
    if not request.json or 'note' not in request.json:
        return abort(400, description="JSON body with 'note' required")

    try:
        new_note = int(request.json['note'])
        if not (0 <= new_note <= 10):
            return abort(400, description="Note must be between 0 and 10")
        
        # Mise à jour
        result = mazes_collection.update_one(
            {"_id": ObjectId(maze_id)},
            {"$set": {"note": new_note}}
        )
        
        if result.matched_count == 0:
            return abort(404, description="Maze not found")

        return jsonify({"status": "success", "new_note": new_note}), 200

    except ValueError:
        return abort(400, description="Note must be an integer")
    except Exception as e:
        return abort(500, description=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)