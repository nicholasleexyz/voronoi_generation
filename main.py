from flask import Flask, render_template, request, redirect, url_for
import base64
import io
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from scipy.spatial.distance import cdist

# from functools import reduce

from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# TODO:

# seedable RNG
# sharable link button

# toggle for outline/grout
# toggle for tillable option
# display to show the texture being tiled
# texture scale slider for tiling display

# color pallette selection dropdown
# buy me a coffee link/button

@app.route('/')
def test():
    return redirect(url_for("generate", width=128, height=128, seed=1))

@app.route('/gen/', methods=["POST","GET"])
def generate():
    seed = int(request.args.get('seed'))

    width = int(request.args.get('width'))
    height = int(request.args.get('height'))

    min_resolution = 64
    max_resolution = 1024
    if width > max_resolution:
        width = max_resolution
    if height > max_resolution:
        height = max_resolution
    if width < min_resolution:
        width = min_resolution
    if height < min_resolution:
        height = min_resolution

    np.random.seed(seed)

    def calculate_distances(args):
        pixel_chunk, cell_points = args
        return cdist(pixel_chunk, cell_points)

    def generate_voronoi(width, height, num_cells, border_size=1):
        # Generate random cell points
        cell_points = np.random.rand(num_cells, 2) * np.array([width, height])

        # Create a grid of pixels
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        pixel_coordinates = np.column_stack((x.ravel(), y.ravel()))

        # Split pixel coordinates into chunks for parallel processing
        chunk_size = height // 4
        pixel_chunks = [(pixel_coordinates[i:i+chunk_size, :], cell_points) for i in range(0, height*width, chunk_size)]

        # Calculate distance from each pixel to each cell point using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            distances_chunks = list(executor.map(calculate_distances, pixel_chunks))

        distances = np.concatenate(distances_chunks, axis=0)

        # Assign each pixel to the closest cell
        voronoi_labels = np.argmin(distances, axis=1)

        # Create an image with different colors for each cell
        voronoi_image = np.zeros((height * width, 3), dtype=np.uint8)
        colors = np.random.randint(0, 256, (num_cells, 3), dtype=np.uint8)

        voronoi_image[:, :] = colors[voronoi_labels]

        # Reshape the image array to match the height and width
        voronoi_image = voronoi_image.reshape((height, width, 3))

        # Add black border to each cell
        mask = voronoi_labels.reshape((height, width))
        border_mask = (np.roll(mask, 1, axis=0) != mask) | (np.roll(mask, 1, axis=1) != mask)
        voronoi_image[border_mask] = [0, 0, 0]

        return voronoi_image

    num_cells = 50

    voronoi_pattern = generate_voronoi(width, height, num_cells)

    image = Image.fromarray(voronoi_pattern)
    data = io.BytesIO()
    image.save(data, "PNG")

    #Then encode the saved image file.
    encoded_img_data = base64.b64encode(data.getvalue())

    return render_template("index.html", img_data=encoded_img_data.decode('utf-8'), width=width, height=height, seed=str(seed))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)