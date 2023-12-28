from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import base64
import io
import math
import random
import numpy as np

app = Flask(__name__)

@app.route('/')
def test():
    return redirect(url_for("generate", rows=4, columns=4, debug=True))

@app.route('/gen/', methods=["GET"])
def generate():
    rows = int(request.args.get('rows'))
    columns = int(request.args.get('columns'))
    debug = request.args.get('debug') == 'True'

    width = 256
    height = 256

    # checkered = [(0, 0, 0) if (x * columns // width) % 2 == (y * rows // height) % 2 else (256, 256, 256) for y in range(height) for x in range(width)]

    centerCoordinates = []

    # l = []
    for y in range(height):
        for x in range(width):
            # dx = x * columns // width
            # dy = y * rows // height

            # val = (100, 100, 100)
            dw = width // columns
            dh = height // rows

            # grid
            # val = (0, 0, 0) if (x % dw == 0 or y % dh == 0 or x % dw == dw - 1 or y % dh == dh - 1) else val

            # center dots
            if (x + dw // 2) % dw == 0 and (y + dh // 2) % dh == 0:
                # val = (255, 255, 255)
                centerCoord = np.array([x, y])
                centerCoordinates.append(centerCoord)

            # val = (255, 255, 255) if (x + dw // 2) % dw == 0 and (y + dh // 2) % dh == 0 else val

            # l.append(val)

    # cell_colors = [(255, 0 , 0) if i % 2 == i // columns % 2 else (0, 255, 255) for i in range(len(centerCoordinates))]
    cell_colors = [(random.randrange(256), random.randrange(256), random.randrange(256)) for i in range(len(centerCoordinates))]
    cell_coordinates = [centerCoord + np.array([random.randrange(-(width // (columns)), (width // (columns))) // 2, random.randrange(-(height // rows), (height // rows))]) // 2 for centerCoord in centerCoordinates]

    pix = []
    for y in range(height):
        for x in range(width):
            # col = l[y * height + x]
            pixelCoord = np.array([x, y])
            lastDist = math.dist(cell_coordinates[0], pixelCoord)
            col = cell_colors[0]
            for i in range(len(cell_coordinates)):
                cellCoord = cell_coordinates[i]
                dist = math.dist(cellCoord, pixelCoord)
                # dist = np.linalg.norm(center - pixelCoord)
                if(dist < lastDist):
                    lastDist = dist
                    col = cell_colors[i]
                    # col = (0, 255, 0, 255)
            pix.append(col)

    if debug:
        for y in range(height):
            for x in range(width):

                pixelCoord = np.array([x, y])

                # grid
                if x % dw == 0 or y % dh == 0 or x % dw == dw - 1 or y % dh == dh - 1:
                    pix[y*height+x] = (0, 0, 0)

                for coord in cell_coordinates:
                    dist = math.dist(coord, pixelCoord)
                    if(dist < 2):
                        pix[y * height + x] = (255,255,255)

                dw = width // columns
                dh = height // rows

    img = Image.new('RGB', (width, height))
    img.putdata(pix)

    data = io.BytesIO()

    #First save image as in-memory.
    # img.save(data, "JPEG")
    img.save(data, "PNG")

    #Then encode the saved image file.
    encoded_img_data = base64.b64encode(data.getvalue())
    return render_template("index.html", img_data=encoded_img_data.decode('utf-8'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)