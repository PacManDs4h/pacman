from flask import Flask, request, jsonify
import sys
sys.path.insert(0, "src/recursive_backtracking/")
from maze import Maze
from json_maze import getJson



app = Flask(__name__)


@app.route("/generate", methods=["GET"])

def generate():
        # paramètres par défaut
    width = int(request.args.get("width", 39))
    height = int(request.args.get("height", 19))
    nbcycle = int(request.args.get("nbcycle", 10))
    nb_wrap_tunnels = int(request.args.get("nb_wrap_tunnels", 2))
    nb_center_tunnels = int(request.args.get("nb_center_tunnels", 5))

    maze = Maze(width, height, nbcycle, nb_wrap_tunnels, nb_center_tunnels)
    maze.generate_maze()

    return getJson(maze)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


