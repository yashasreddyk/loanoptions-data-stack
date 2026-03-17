import os
from PIL import Image
import math

img_dir = "slide_images"
images = []
for i in range(1, 58):
    path = os.path.join(img_dir, f"Slide{i}.PNG")
    if os.path.exists(path):
        images.append(Image.open(path))

if not images:
    print("No images found.")
    exit()

# assuming all slides have same dimensions
w, h = images[0].size
# scale down by 4 to save memory and make a manageable grid
scale = 0.25
w_scaled = int(w * scale)
h_scaled = int(h * scale)

cols = 6
rows = math.ceil(len(images) / cols)

grid = Image.new('RGB', size=(cols * w_scaled, rows * h_scaled), color=(255, 255, 255))

for i, img in enumerate(images):
    img = img.resize((w_scaled, h_scaled))
    grid.paste(img, box=(i % cols * w_scaled, i // cols * h_scaled))

grid.save("slide_grid.png")
print("Saved slide_grid.png")
