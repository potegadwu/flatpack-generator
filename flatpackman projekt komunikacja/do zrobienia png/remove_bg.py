from PIL import Image
import os
import glob

INPUT_DIR = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\do zrobienia png"
OUTPUT_DIR = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\png bez tla"

os.makedirs(OUTPUT_DIR, exist_ok=True)

extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif')
image_files = []
for ext in extensions:
    image_files.extend(glob.glob(os.path.join(INPUT_DIR, ext)))
image_files = [f for f in image_files if not f.endswith('remove_bg.py')]

print(f"Found {len(image_files)} images to process")

def remove_background(img, threshold=40):
    """Remove white/light background using flood fill from edges (optimized)."""
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size
    
    # Create a set for visited pixels and a stack for flood fill
    visited = set()
    stack = []
    
    # Seed from all edge pixels
    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(1, height - 1):
        stack.append((0, y))
        stack.append((width - 1, y))
    
    while stack:
        x, y = stack.pop()
        
        if (x, y) in visited:
            continue
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
            
        r, g, b, a = pixels[x, y]
        
        # Skip if already transparent
        if a == 0:
            visited.add((x, y))
            continue
        
        # Check if pixel is light/white (background)
        if r > 255 - threshold and g > 255 - threshold and b > 255 - threshold:
            pixels[x, y] = (r, g, b, 0)
            visited.add((x, y))
            # Add neighbors
            stack.append((x - 1, y))
            stack.append((x + 1, y))
            stack.append((x, y - 1))
            stack.append((x, y + 1))
        else:
            visited.add((x, y))
    
    return img

for filepath in image_files:
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.png")
    
    print(f"Processing: {filename}")
    
    try:
        img = Image.open(filepath)
        result = remove_background(img, threshold=45)
        result.save(output_path, "PNG")
        print(f"  Saved: {output_path}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone!")
