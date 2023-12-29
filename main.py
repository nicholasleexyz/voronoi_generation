from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import base64
import io
# import math
import random
import numpy as np
import numpy.typing as npt

app = Flask(__name__)

@app.route('/')
def test():

    def get_surrounding_elements(array, index, width):

        def get_surrounding_indexes(_index, _width, _length):
            match (_index, _width, _length):
                case i, w, _ if i == 0: # top left
                    return [i + 1, w, w + 1]
                case i, w, _ if i == w - 1: # top right
                    return [w - 2, w * 2 - 2, w * 2 - 1]
                case i, w, l if i == l - w: # bottom left
                    return [l - w * 2, l - w * 2 + 1, l - w + 1]
                case i, w, l if i == l - 1: # bottom right
                    return [l - w - 2, l - w - 1, l - 2]
                case i, w, _ if i < w: # top edge
                    return [i - 1, i + 1, i + w - 1, i + w, i + w + 1]
                case i, w, _ if i % w == 0: # left edge
                    return [i - w, i - w + 1, i + 1, i + w, i + w + 1]
                case i, w, _ if (i + 1) % w == 0: # right edge
                    return [i - w - 1, i - w, i - 1, i + w - 1, i + w]
                case i, w, l if i > (l - w - 1): # bottom edge
                    return [i - w - 1, i - w, i - w + 1, i - 1, i + 1]
                case _:
                    return [i - w - 1, i - w, i - w + 1, i - 1, i + 1, i + w - 1, i + w, i + w + 1]

        for y in range(4):
            for x in range(4):
                index = y * 4 + x
                val  = get_surrounding_indexes(index, 4, 16);
                print(f"Index: {index}, Value: {val}")

    get_surrounding_elements([], 0, 4)

    return redirect(url_for("generate", rows=4, columns=4, debug=True))
#    public static T[] GetSurroundingElements<T>(this T[] a, int index, int width)
#     {
#         var length = a.Length;
#         Debug.Assert((length % width == 0), "Array length is not divisible by width so could not calculate surrounding elements.");

#         //corners
#         var isTopLeft = index == 0;
#         var isTopRight = index == width - 1;
#         var isBottomLeft = index == length - width;
#         var isBottomRight = index == length - 1;

#         var isLeftEdge = index % width == 0;
#         var isRightEdge = (index + 1) % width == 0;
#         var isTopEdge = index < width;
#         var isBottomEdge = index > (length - width - 1);

#         if (isTopLeft)
#             return new T[] { a[index + 1], a[width], a[width + 1] };
#         else if (isTopRight)
#             return new T[] { a[width - 2], a[(width * 2) - 2], a[(width * 2) - 1] };
#         else if (isBottomLeft)
#             return new T[] { a[length - (width * 2)], a[(length - (width * 2)) + 1], a[(length - width) + 1] };
#         else if (isBottomRight)
#             return new T[] { a[length - width - 2], a[length - width - 1], a[length - 2] };
#         else if (isTopEdge)
#             return new T[] { a[index - 1], a[index + 1], a[(index + width) - 1], a[index + width], a[index + width + 1] };
#         else if (isBottomEdge)
#             return new T[] { a[index - width - 1], a[index - width], a[(index - width) + 1], a[index - 1], a[index + 1] };
#         else if (isLeftEdge)
#             return new T[] { a[index - width], a[(index - width) + 1], a[index + 1], a[index + width], a[index + width + 1] };
#         else if (isRightEdge)
#             return new T[] { a[index - width - 1], a[index - width], a[index - 1], a[(index + width) - 1], a[index + width] };
#         else
#             return new T[] { a[index - width - 1], a[index - width], a[(index - width) + 1], a[index - 1], a[index + 1], a[(index + width) - 1], a[index + width], a[index + width + 1] };
#     }

@app.route('/gen/', methods=["GET"])
def generate():
    def gen_rand_color():
        r = random.randrange(256)
        g = random.randrange(256)
        b = random.randrange(256)
        return (r, g, b)

    rows = int(request.args.get('rows'))
    columns = int(request.args.get('columns'))
    debug = request.args.get('debug') == 'True'

    width = 256
    height = 256

    centerCoordinates = []

    for y in range(height):
        for x in range(width):
            dw = width // columns
            dh = height // rows

            # center dots
            if (x + dw // 2) % dw == 0 and (y + dh // 2) % dh == 0:
                centerCoord = np.array([x, y])
                centerCoordinates.append(centerCoord)

    cell_colors = [gen_rand_color() for i in range(len(centerCoordinates))]
    cell_coordinates = [centerCoord + np.array([random.randrange(-(width // (columns)), (width // (columns))) // 2, random.randrange(-(height // rows), (height // rows))]) // 2 for centerCoord in centerCoordinates]

    pix = []
    for y in range(height):
        for x in range(width):
            pixelCoord = np.array([x, y])
            lastDist = np.linalg.norm(cell_coordinates[0] - pixelCoord)
            col = cell_colors[0]
            for i in range(len(cell_coordinates)):
                cellCoord = cell_coordinates[i]
                dist = np.linalg.norm(cellCoord - pixelCoord)
                if(dist < lastDist):
                    lastDist = dist
                    col = cell_colors[i]
            pix.append(col)

    if debug:
        for y in range(height):
            for x in range(width):

                pixelCoord = np.array([x, y])

                # grid
                if x % dw == 0 or y % dh == 0 or x % dw == dw - 1 or y % dh == dh - 1:
                    pix[y*height+x] = (0, 0, 0)

                for coord in cell_coordinates:
                    dist = np.linalg.norm(coord - pixelCoord)
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