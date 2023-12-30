from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import base64
import io
import random
import numpy as np
import numpy.typing as npt
from functools import reduce

app = Flask(__name__)

@app.route('/')
def test():
    # return redirect(url_for("generate", rows=4, columns=4, debug=True))
    return redirect(url_for("generate", rows=4, columns=4, debug=True))

@app.route('/gen/', methods=["POST","GET"])
def generate():

    def get_surrounding_indexes(_index, _width, _length):
        match (_index, _width, _length):
            case i, w, _ if i == 0: # top left
                return [i, i + 1, w, w + 1]
            case i, w, _ if i == w - 1: # top right
                return [i, w - 2, w * 2 - 2, w * 2 - 1]
            case i, w, l if i == l - w: # bottom left
                return [i, l - w * 2, l - w * 2 + 1, l - w + 1]
            case i, w, l if i == l - 1: # bottom right
                return [i, l - w - 2, l - w - 1, l - 2]
            case i, w, _ if i < w: # top edge
                return [i, i - 1, i + 1, i + w - 1, i + w, i + w + 1]
            case i, w, _ if i % w == 0: # left edge
                return [i, i - w, i - w + 1, i + 1, i + w, i + w + 1]
            case i, w, _ if (i + 1) % w == 0: # right edge
                return [i, i - w - 1, i - w, i - 1, i + w - 1, i + w]
            case i, w, l if i > (l - w - 1): # bottom edge
                return [i, i - w - 1, i - w, i - w + 1, i - 1, i + 1]
            case _:
                return [i, i - w - 1, i - w, i - w + 1, i - 1, i + 1, i + w - 1, i + w, i + w + 1]

    def gen_rand_color():
        r = random.randrange(256)
        g = random.randrange(256)
        b = random.randrange(256)
        return (r, g, b)

    def rand_offset_coord(coord):
        offset_x = width // columns // 2
        offset_y = height // rows // 2
        return coord + np.array([random.randrange(-offset_x, offset_x), random.randrange(-offset_y, offset_y)])


    rows = int(request.args.get('rows'))
    columns = int(request.args.get('columns'))
    debug = request.args.get('debug') == 'on'

    width = 256
    height = 256

    def gen_grad_color(x, y):
        return (x*(width//columns),y*(height//rows),0)

    colors = [gen_rand_color() for y in range(rows) for x in range(columns)]
    # colors = [gen_grad_color(x, y) for y in range(rows) for x in range(columns)]

    centerCoordinates = []

    for y in range(height):
        for x in range(width):
            dw = width // columns
            dh = height // rows

            # center dots
            if (x + dw // 2) % dw == 0 and (y + dh // 2) % dh == 0:
                centerCoord = rand_offset_coord(np.array([x, y]))
                # centerCoord = np.array([x, y])
                centerCoordinates.append(centerCoord)

    def voronoi(x, y):
        _y = y // (height // rows)
        _x = x // (width // columns)
        i = _y * columns + _x


        pixelCoord = np.array([x, y])
        surrounding_indexes = get_surrounding_indexes(i, columns, rows*columns);

        shortestDist = sorted([(idx, np.linalg.norm(centerCoordinates[idx] - pixelCoord)) for idx in surrounding_indexes], key=lambda x: x[1], reverse=False)[0]

        shortestDistIndex = shortestDist[0]
        shortestDistValue = shortestDist[1]

        coord_col = (255, 255, 255)
        grid_col = (127, 127, 127)

        if debug:
            dw = width // columns
            dh = height // rows

            if shortestDistValue < 1:
                col = coord_col
            elif x % dw == 0 or y % dh == 0: # grid
                col = grid_col
            else:
                col = colors[shortestDistIndex]
        else:
            col = colors[shortestDistIndex]


        return col

    pix = [voronoi(x, y) for y in range(height) for x in range(width)]

    img = Image.new('RGB', (width, height))
    img.putdata(pix)

    data = io.BytesIO()

    #First save image as in-memory.
    # img.save(data, "JPEG")
    img.save(data, "PNG")

    #Then encode the saved image file.
    encoded_img_data = base64.b64encode(data.getvalue())
    print(f"Debug Mode: {debug}")
    return render_template("index.html", img_data=encoded_img_data.decode('utf-8'), rows=rows, columns=columns, debug=debug)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)