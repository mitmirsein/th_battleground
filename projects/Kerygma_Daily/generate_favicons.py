from PIL import Image, ImageOps
import os

def create_favicon():
    # Configuration
    source_path = 'icons/new_source.png'
    
    # Colors
    white = (255, 255, 255, 255)       # Background
    deep_slate = (30, 41, 59, 255)     # Foreground (#1e293b)
    
    # All standard sizes (Favicon + PWA)
    sizes = [16, 32, 48, 64, 72, 96, 128, 144, 152, 192, 384, 512]
    
    # Load Source
    try:
        src = Image.open(source_path)
    except Exception as e:
        print(f"Error loading source: {e}")
        return

    # 1. Resize to Master Size (512x512)
    # The source is 1024x1024, so we resize down cleanly
    src_resized = src.resize((512, 512), Image.Resampling.LANCZOS)
    
    # 2. Logic: White BG, Deep Slate Lines
    # Convert to Grayscale to get "Ink Density"
    gray = src_resized.convert("L")
    
    # Invert grayscale: 
    # Original: White(255) BG, Dark(0) Lines
    # Inverted: Black(0) BG, White(255) Lines -> This becomes our Mask for the Deep Slate color
    mask = ImageOps.invert(gray)
    
    # Create Solid Color Layers
    bg_layer = Image.new("RGBA", (512, 512), white)
    fg_layer = Image.new("RGBA", (512, 512), deep_slate)
    
    # Composite: Put FG on top of BG using Mask
    master = Image.composite(fg_layer, bg_layer, mask)
    
    # Save Master
    master.save("icons/favicon-master-bg.png")
    print("Created master: icons/favicon-master-bg.png")

    # Generate Sizes
    for size in sizes:
        # Resize from master
        icon = master.resize((size, size), Image.Resampling.LANCZOS)
        
        # Naming convention
        if size <= 64:
            filename = f"icons/favicon-{size}.png"
        else:
            filename = f"icons/icon-{size}.png"
            
        icon.save(filename)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    create_favicon()
