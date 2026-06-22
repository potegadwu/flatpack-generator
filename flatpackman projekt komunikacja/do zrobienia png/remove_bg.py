from PIL import Image
import os
import glob
from collections import Counter

INPUT_DIR = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\do zrobienia png"
OUTPUT_DIR = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\png bez tla"

os.makedirs(OUTPUT_DIR, exist_ok=True)

extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif')
image_files = []
for ext in extensions:
    image_files.extend(glob.glob(os.path.join(INPUT_DIR, ext)))
image_files = [f for f in image_files if not f.endswith('remove_bg.py')]

print(f"Found {len(image_files)} images to process")

def remove_background(img, threshold=30):
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    corners = []
    for x in [0, 1, width-2, width-1]:
        for y in [0, 1, height-2, height-1]:
            if 0 <= x < width and 0 <= y < height:
                corners.append(pixels[x, y][:3])

    bg_color = Counter(corners).most_common(1)[0][0]
    print(f"  Background color: RGB{bg_color}")

    visited = set()
    stack = []

    def is_bg(x, y):
        if (x, y) in visited:
            return False
        if x < 0 or x >= width or y < 0 or y >= height:
            return False
        r, g, b, a = pixels[x, y]
        if a == 0:
            return True
        return (abs(r - bg_color[0]) < threshold and
                abs(g - bg_color[1]) < threshold and
                abs(b - bg_color[2]) < threshold)

    for x in range(width):
        if is_bg(x, 0):
            stack.append((x, 0))
        if is_bg(x, height - 1):
            stack.append((x, height - 1))
    for y in range(1, height - 1):
        if is_bg(0, y):
            stack.append((0, y))
        if is_bg(width - 1, y):
            stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        if not is_bg(x, y):
            continue

        visited.add((x, y))
        r, g, b, a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                stack.append((nx, ny))

    return img

for filepath in image_files:
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.png")

    print(f"Processing: {filename}")
    try:
        img = Image.open(filepath)
        result = remove_background(img, threshold=35)
        result.save(output_path, "PNG")
        print(f"  Saved: {output_path}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone!")
