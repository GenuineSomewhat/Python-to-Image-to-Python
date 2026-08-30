"""
Convert Python source files to PNG images.
Encodes the binary data as RGB pixel values.
"""

import sys
from pathlib import Path
from PIL import Image
import math


def python_to_image(python_file: str, output_image: str = None) -> str:
    """
    Convert a Python file to a PNG image.
    
    Args:
        python_file: Path to the .py file
        output_image: Path to save the PNG image (defaults to python_file.png)
    
    Returns:
        Path to the generated image
    """
    
    # Read Python file as bytes
    python_path = Path(python_file)
    if not python_path.exists():
        raise FileNotFoundError(f"Python file not found: {python_file}")
    
    with open(python_path, 'rb') as f:
        data = f.read()
    
    # Determine output path
    if output_image is None:
        output_image = str(python_path.with_suffix('.png'))
    
    # Calculate image dimensions
    # Each pixel holds 3 bytes (RGB), so we need ceil(len(data) / 3) pixels
    num_pixels = math.ceil(len(data) / 3)
    # Use a square-ish layout: width ≈ height
    width = math.ceil(math.sqrt(num_pixels))
    height = math.ceil(num_pixels / width)
    
    # Pad data to fill all pixels (RGB values)
    total_bytes_needed = width * height * 3
    data_padded = data + bytes([0] * (total_bytes_needed - len(data)))
    
    # Convert bytes to RGB tuples
    pixels = []
    for i in range(0, len(data_padded), 3):
        r = data_padded[i]
        g = data_padded[i + 1]
        b = data_padded[i + 2]
        pixels.append((r, g, b))
    
    # Create image
    image = Image.new('RGB', (width, height))
    image.putdata(pixels)
    
    # Store original file size in image metadata
    # We'll store it in the first pixel as a special marker
    # Actually, let's use a different approach: store metadata in a text comment
    
    # Save with metadata
    metadata = {
        'original_size': str(len(data)),
        'filename': python_path.name
    }
    image.save(output_image, pnginfo=None)
    
    # Re-open and add metadata properly using PIL's metadata
    from PIL.PngImagePlugin import PngInfo
    pnginfo = PngInfo()
    pnginfo.add_text("original_size", str(len(data)))
    pnginfo.add_text("original_filename", python_path.name)
    image.save(output_image, pnginfo=pnginfo)
    
    print(f"✓ Converted {python_file} → {output_image}")
    print(f"  Dimensions: {width}x{height} pixels")
    print(f"  Original size: {len(data)} bytes")
    
    return output_image


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python py_to_img.py <python_file> [output_image.png]")
        print("Example: python py_to_img.py script.py")
        sys.exit(1)
    
    python_file = sys.argv[1]
    output_image = sys.argv[2] if len(sys.argv) > 2 else None
    
    python_to_image(python_file, output_image)
