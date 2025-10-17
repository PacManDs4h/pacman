from create_image import *
from maze import *

data = json.loads(getJson())
createImage(data).show()