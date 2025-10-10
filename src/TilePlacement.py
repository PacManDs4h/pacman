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

empty_tile = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]
plus_tile = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

TriangleUp_tile = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 0]
]
TriangleDown_tile = [
    [0, 0, 0],
    [1, 1, 1],
    [0, 1, 0]
]
TriangleLeft_tile = [
    [0, 1, 0],
    [0, 1, 1],
    [0, 1, 0]
]
TriangleRight_tile = [
    [0, 1, 0],
    [1, 1, 0],
    [0, 1, 0]
]
CornerUpLeft_tile = [
    [0, 1, 0],
    [0, 1, 1],
    [0, 0, 0]
]
CornerDownLeft_tile = [
    [0, 0, 0],
    [0, 1, 1],
    [0, 1, 0]
]
CornerUpRight_tile = [
    [0, 1, 0],
    [1, 1, 0],
    [0, 0, 0]
]
CornerDownRight_tile = [
    [0, 0, 0],
    [1, 1, 0],
    [0, 1, 0]
]
VerticalLine_tile = [
    [0, 1, 0],
    [0, 1, 0],
    [0, 1, 0]
]
HorizontalLine_tile = [
    [0, 0, 0],
    [1, 1, 1],
    [0, 0, 0]
]

empty_image = create_tile(empty_tile)
plus_image = create_tile(plus_tile)
TriangleUp_image = create_tile(TriangleUp_tile)
TriangleDown_image = create_tile(TriangleDown_tile)
TriangleLeft_image = create_tile(TriangleLeft_tile)
TriangleRight_image = create_tile(TriangleRight_tile)
CornerUpLeft_image = create_tile(CornerUpLeft_tile)
CornerDownLeft_image = create_tile(CornerDownLeft_tile)
CornerUpRight_image = create_tile(CornerUpRight_tile)
CornerDownRight_image = create_tile(CornerDownRight_tile)
VerticalLine_image = create_tile(VerticalLine_tile)
HorizontalLine_image = create_tile(HorizontalLine_tile)

tiles = [empty_image, plus_image, TriangleUp_image, TriangleDown_image, TriangleLeft_image, TriangleRight_image, CornerUpLeft_image,
          CornerDownLeft_image, CornerUpRight_image, CornerDownRight_image, VerticalLine_image, HorizontalLine_image]


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
        combined_image.paste(tiles[int(labyrinthe[x][y])], (tile_width*x, tile_height*y))

combined_image.show(title="maze")
combined_image.save("labyrinthe.png")
