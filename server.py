from flask import Flask, request, jsonify
from src/recursive_bactracking.py  


app = Flask(__name__)

@app.route("/generate", methods=["GET"])
def generate():
    # paramètres par défaut
    width = int(request.args.get("width", 20))
    height = int(request.args.get("height", 15))
    braid = float(request.args.get("braid", 0.7))

    # appel à ta fonction Python qui génère le labyrinthe

    # on renvoie le résultat au format JSON
    return jsonify({
        "width": width,
        "height": height,
        "braid": braid,

    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
