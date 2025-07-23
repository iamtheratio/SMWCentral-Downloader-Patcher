#!/usr/bin/env python3
"""
Generate PNG icons for Linux from existing ICO/ICNS files
This script converts the icon to multiple PNG sizes for Linux desktop integration
"""

import os
import sys
from pathlib import Path

def generate_linux_icons():
    """Generate PNG icons for Linux from existing icon files"""
    
    # Icon sizes needed for Linux
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    # Paths
    assets_dir = Path("assets")
    icons_dir = assets_dir / "icons"
    
    # Create icons directory if it doesn't exist
    icons_dir.mkdir(exist_ok=True)
    
    print("🐧 Generating Linux PNG icons...")
    
    try:
        # Try to import PIL for icon conversion
        from PIL import Image
        
        # Look for source icon files
        icon_sources = [
            assets_dir / "icon.icns",
            assets_dir / "icon.ico",
            assets_dir / "icon.png"
        ]
        
        source_icon = None
        for icon_path in icon_sources:
            if icon_path.exists():
                source_icon = icon_path
                break
        
        if not source_icon:
            print("❌ No source icon found (icon.icns, icon.ico, or icon.png)")
            return False
        
        print(f"📁 Using source icon: {source_icon}")
        
        # Open source image
        with Image.open(source_icon) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Generate each size
            for size in sizes:
                # Resize image
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                
                # Save PNG
                output_path = icons_dir / f"smwc-downloader-{size}x{size}.png"
                resized.save(output_path, "PNG")
                print(f"✅ Generated: {output_path}")
        
        print("🎉 Linux icons generated successfully!")
        return True
        
    except ImportError:
        print("⚠️  PIL (Pillow) not available - creating placeholder instructions")
        
        # Create a README for manual icon generation
        readme_content = """# Linux Icons for SMWC Downloader

## Icon Requirements
Linux desktop environments expect PNG icons in standard sizes:
- 16x16, 32x32, 48x48, 64x64, 128x128, 256x256, 512x512

## Manual Icon Generation
If you have the source icon file (icon.icns, icon.ico, or icon.png), you can generate Linux icons using:

### Using ImageMagick:
```bash
# Install ImageMagick
sudo apt install imagemagick  # Ubuntu/Debian
sudo dnf install ImageMagick  # Fedora
sudo pacman -S imagemagick    # Arch

# Generate icons
for size in 16 32 48 64 128 256 512; do
    convert assets/icon.icns -resize ${size}x${size} assets/icons/smwc-downloader-${size}x${size}.png
done
```

### Using GIMP:
1. Open icon.icns or icon.ico in GIMP
2. Scale image to each required size
3. Export as PNG with naming: smwc-downloader-{size}x{size}.png

### Online Conversion:
- Use online ICO/ICNS to PNG converters
- Generate the required sizes manually

## Installation Location
PNG icons should be placed in:
- `/usr/share/icons/hicolor/{size}x{size}/apps/smwc-downloader.png`
- Or in user directory: `~/.local/share/icons/hicolor/{size}x{size}/apps/smwc-downloader.png`
"""
        
        with open(icons_dir / "README.md", "w") as f:
            f.write(readme_content)
        
        print("📝 Created README.md with manual icon generation instructions")
        return True

if __name__ == "__main__":
    success = generate_linux_icons()
    sys.exit(0 if success else 1)
