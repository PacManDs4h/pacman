from create_image import createImage
import json

from urllib.request import urlopen

WIDTH = 39
HEIGHT = 19
NB_CYCLES = 10
NUM_WRAP_TUNNELS = 2
NUM_CENTER_TUNNELS = 5

url = f"https://pacmaz-s1-o.onrender.com/generate?width={WIDTH}&height={HEIGHT}&nb_cycle={NB_CYCLES}&num_tunnels_wrap={NUM_WRAP_TUNNELS}&num_tunnels_centre={NUM_CENTER_TUNNELS}"


response = urlopen(url)

data_json = json.loads(response.read())

createImage(data_json).show()
