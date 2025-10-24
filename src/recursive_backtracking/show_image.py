from create_image import createImage
import json

from urllib.request import urlopen

WIDTH = 39
HEIGHT = 19
NB_CYCLES = 10
NUM_WRAP_TUNNELS = 2
NUM_CENTER_TUNNELS = 5

# maze = Maze(WIDTH, HEIGHT, NB_CYCLES, NUM_WRAP_TUNNELS, NUM_CENTER_TUNNELS)
# maze.generate_maze()

url = "https://pacmaz-s1-o.onrender.com/generate"
# url = "https://pacmaz-s1-o.onrender.com/generate?width={WIDTH}&height={HEIGHT}&height={NB_CYCLES}"


response = urlopen(url)

data_json = json.loads(response.read())

createImage(data_json).show()
