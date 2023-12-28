from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import base64
import io

app = Flask(__name__)

@app.route('/')
def test():
    return redirect(url_for("generate", rows=4, columns=4))

# checkered
# grid lines
# use rng
# place dots at center of cells

@app.route('/gen/', methods=["GET"])
def generate():
    rows = int(request.args.get('rows'))
    columns = int(request.args.get('columns'))
    # r = request.args.get('rows')
    # c = request.args.get('columns')
    # rows = int(r) if r else 8
    # columns = int(c) if c else 8

    width = 1024
    height = 1024

    # checkered = [(0, 0, 0) if (x * columns // width) % 2 == (y * rows // height) % 2 else (256, 256, 256) for y in range(height) for x in range(width)]

    l = []
    for y in range(height):
        for x in range(width):
            dx = x * columns // width
            dy = y * rows // height

            # val = (0,0,0) if dx % 2 == dy % 2 else (255, 255, 255)
            # val = (0, 127, 55)
            val = (255, 255, 255)
            dw = width // columns
            dh = height // rows
            val = (127, 127, 127) if (x % dw == 0 or y % dh == 0 or x % dw == dw - 1 or y % dh == dh - 1) else val
            val = (0,255,0) if (x + dw // 2) % dw == 0 and (y + dh // 2) % dh == 0 else val

            l.append(val)


    img = Image.new('RGB', (width, height))
    # img.putdata(checkered)
    img.putdata(l)

    data = io.BytesIO()

    #First save image as in-memory.
    # img.save(data, "JPEG")
    img.save(data, "PNG")

    #Then encode the saved image file.
    encoded_img_data = base64.b64encode(data.getvalue())
    return render_template("index.html", img_data=encoded_img_data.decode('utf-8'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)