from recursive_backtracking.json_maze import getJson
from recursive_backtracking.maze import Maze
from flask import Flask, request, jsonify


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


@app.route("/", methods=["GET"])
def index():
    return "Maze API is running. Use GET /generate", 200


@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200
