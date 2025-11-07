from PIL import Image, ImageDraw


def createImage(data):
    taille_case = 20

    image = Image.new(
        "RGB", (data["width"] * taille_case, data["height"] * taille_case), "white")
    draw = ImageDraw.Draw(image)

    for y in range(data["height"]):
        for x in range(data["width"]):
            couleur = (0, 0, 0) if data["maze"][y][x] == 1 else (255, 255, 255)

            draw.rectangle([x * taille_case, y * taille_case, (x + 1)
                           * taille_case, (y + 1) * taille_case], fill=couleur)
    # image.show()
    return image
