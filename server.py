from maze import Maze
from json_maze import getJson
from flask import Flask, request, jsonify
import sys
sys.path.insert(0, "src/recursive_backtracking/")


app = Flask(__name__)


@app.route("/generate", methods=["GET"])
def generate():
    maze = Maze(19, 39, 10, 2, 5)
    maze.generate_maze()

    return getJson(maze)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
