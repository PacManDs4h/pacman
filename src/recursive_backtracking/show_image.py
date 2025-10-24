from create_image import createImage
import json
from maze import Maze
from json_maze import getJson
from urllib.request import urlopen

WIDTH = 28
HEIGHT = 36
NB_CYCLES = 10
NUM_WRAP_TUNNELS = 2
NUM_CENTER_TUNNELS = 5


maze = Maze(WIDTH, HEIGHT, NB_CYCLES, NUM_WRAP_TUNNELS, NUM_CENTER_TUNNELS)
maze.generate_maze()
data = json.loads(getJson(maze))
createImage(data).show()
exit()


url = f"https://pacmaz-s1-o.onrender.com/generate?width={WIDTH}&height={HEIGHT}&nb_cycle={NB_CYCLES}&num_tunnels_wrap={NUM_WRAP_TUNNELS}&num_tunnels_centre={NUM_CENTER_TUNNELS}"


response = urlopen(url)

data_json = json.loads(response.read())
print(data_json["symetrie"])

createImage(data_json).show()
