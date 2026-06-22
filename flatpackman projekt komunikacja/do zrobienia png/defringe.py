from PIL import Image, ImageFilter, ImageOps
import os
import glob

def clean_edges(img_path, output_path):
    img = Image.open(img_path).convert("RGBA")
    width, height = img.size
    
    # 1. Create eroded alpha mask
    # MinFilter(3) takes the minimum alpha in a 3x3 window, which effectively shrinks the alpha mask by 1 pixel.
    r, g, b, a = img.split()
    a_eroded = a.filter(ImageFilter.MinFilter(3))
    
    # Let's do a pixel-by-pixel cleanup on the original image using the eroded alpha
    # and also remove whitish halo pixels
    pixels = img.load()
    eroded_pixels = a_eroded.load()
    
    new_img = Image.new("RGBA", (width, height))
    new_pixels = new_img.load()
    
    for y in range(height):
        for x in range(width):
            cr, cg, cb, ca = pixels[x, y]
            eroded_a = eroded_pixels[x, y]
            
            # If eroded alpha is 0, we can discard this pixel (removes the outermost 1px shell)
            if eroded_a == 0:
                new_pixels[x, y] = (cr, cg, cb, 0)
                continue
                
            # If the pixel is near a transparent area (eroded_a < 255) and is whitish, we make it transparent or reduce its alpha
            if eroded_a < 255:
                # Whitish halo check
                # Typically, white fringes have high R, G, B and low saturation
                if cr > 160 and cg > 160 and cb > 160:
                    # Let's blend it or make it transparent
                    # If it's very white, reduce its alpha significantly
                    brightness = (cr + cg + cb) / 3
                    whiteness = 255 - max(abs(cr - cg), abs(cg - cb), abs(cb - cr))
                    if brightness > 180 and whiteness > 240:
                        # It's a white fringe pixel, make it transparent
                        new_pixels[x, y] = (cr, cg, cb, 0)
                        continue
            
            new_pixels[x, y] = (cr, cg, cb, ca)
            
    # Smooth the final alpha channel a bit to avoid jagged edges
    r_n, g_n, b_n, a_n = new_img.split()
    a_smooth = a_n.filter(ImageFilter.GaussianBlur(radius=0.5))
    final_img = Image.merge("RGBA", (r_n, g_n, b_n, a_smooth))
    
    final_img.save(output_path, "PNG")
    print(f"Cleaned: {os.path.basename(img_path)} -> {os.path.basename(output_path)}")

# Test on one image
src = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\final logo i postac\Michał 5.png"
dst = r"C:\Users\Malgorzata\Desktop\flatpack-generator\flatpackman projekt komunikacja\final logo i postac\Michał 5_cleaned.png"

if os.path.exists(src):
    clean_edges(src, dst)
else:
    print("Test file not found")
