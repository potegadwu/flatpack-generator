from PIL import Image, ImageFilter
import os
import glob

INPUT_DIR = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\png bez tla"
OUTPUT_DIR = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\png final"

os.makedirs(OUTPUT_DIR, exist_ok=True)

image_files = glob.glob(os.path.join(INPUT_DIR, "*.png"))
print(f"Found {len(image_files)} PNG files")

def process_image(img):
    """Remove watermark and star icons, smooth edges."""
    img = img.convert("RGBA")
    w, h = img.size
    pixels = img.load()
    
    # Step 1: Remove star icon in bottom-right corner
    # The star is a 4-pointed white shape on light gray gradient
    # Scan the bottom-right 200x200 area
    for x in range(max(0, w - 200), w):
        for y in range(max(0, h - 200), h):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            
            # Calculate local brightness vs surroundings
            # Sample a ring around the pixel
            ring_brightness = []
            for d in range(15, 25):
                for angle_x in [-1, 0, 1]:
                    for angle_y in [-1, 0, 1]:
                        nx = x + angle_x * d
                        ny = y + angle_y * d
                        if 0 <= nx < w and 0 <= ny < h:
                            nr, ng, nb, na = pixels[nx, ny]
                            if na > 0:
                                ring_brightness.append((nr + ng + nb) / 3)
            
            if ring_brightness:
                avg_ring = sum(ring_brightness) / len(ring_brightness)
                pixel_brightness = (r + g + b) / 3
                
                # If pixel is significantly brighter than ring, it's a star
                if pixel_brightness > avg_ring + 30 and pixel_brightness > 220:
                    pixels[x, y] = (r, g, b, 0)
    
    # Step 2: Crop bottom to remove text watermark
    new_h = h - 55
    img = img.crop((0, 0, w, new_h))
    
    # Step 3: Smooth alpha channel
    r, g, b, a = img.split()
    a_smooth = a.filter(ImageFilter.GaussianBlur(radius=0.8))
    img = Image.merge("RGBA", (r, g, b, a_smooth))
    
    return img

for filepath in image_files:
    filename = os.path.basename(filepath)
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    print(f"Processing: {filename}")
    try:
        img = Image.open(filepath)
        result = process_image(img)
        result.save(output_path, "PNG")
        print(f"  OK")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone!")
