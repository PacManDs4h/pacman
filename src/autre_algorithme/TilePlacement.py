import random
from PIL import Image, ImageDraw

size = 5

tile_size = 30
tile_width = tile_size * 3 
tile_height = tile_size * 3

def create_tile(grid):
    img = Image.new("RGB", (tile_width, tile_height), "white")
    draw = ImageDraw.Draw(img)
    
    # 0 = mur, 1 = vide
    for i in range(3):
        for j in range(3):
            color = (0, 0, 0) if grid[i][j] == 0 else (255, 255, 255)
            draw.rectangle(
                [j * tile_size, i * tile_size, (j + 1) * tile_size, (i + 1) * tile_size],
                fill=color
            )
    
    return img


tiles = []
tiles.append([ #empty
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
])
tiles.append([ #triangle up
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 0]
])
tiles.append([ #triangle right
    [0, 1, 0],
    [0, 1, 1],
    [0, 1, 0]
])
tiles.append([ #triangle down
    [0, 0, 0],
    [1, 1, 1],
    [0, 1, 0]
])
tiles.append([ #triangle left
    [0, 1, 0],
    [1, 1, 0],
    [0, 1, 0]
])
tiles.append([ #corner up right
    [0, 1, 0],
    [0, 1, 1],
    [0, 0, 0]
])
tiles.append([ #corner right down
    [0, 0, 0],
    [0, 1, 1],
    [0, 1, 0]
])
tiles.append([ #corner down left
    [0, 0, 0],
    [1, 1, 0],
    [0, 1, 0]
])
tiles.append([ #corner left up
    [0, 1, 0],
    [1, 1, 0],
    [0, 0, 0]
])
tiles.append([ #plus
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
])
tiles.append([ #vertical
    [0, 1, 0],
    [0, 1, 0],
    [0, 1, 0]
])
tiles.append([ #horizontal
    [0, 0, 0],
    [1, 1, 1],
    [0, 0, 0]
])


image = []

for i in range(len(tiles)):
    image.append(create_tile(tiles[i]))

combined_width = tile_width * size
combined_height = tile_height * size

combined_image = Image.new("RGB", (combined_width, combined_height), "white")


def randomShape():
    return str(random.randint(0, len(tiles)-1))

with open("maze.txt", "w") as f:
    for i in range(size):
        for n in range(size):
            f.write(randomShape())
            f.write(",")
        f.write("\n")


with open("maze.txt", "r") as fichier:
    labyrinthe = [ligne.strip().split(',') for ligne in fichier]

for y in range(size):
    for x in range(size):
        combined_image.paste(image[int(labyrinthe[y][x])], (tile_width*x, tile_height*y))

combined_image.show(title="maze")
combined_image.save("labyrinthe.png")
