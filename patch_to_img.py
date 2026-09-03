"""
Convert a file to a patch PNG image with metadata header.
Header format: n_<filename>-p_<folder_path>\x00[RGB encoded file data]
"""

import sys
from pathlib import Path
from PIL import Image
import math


def file_to_patch_image(file_path: str, folder_path: str, output_image: str = None) -> str:
    """
    Convert a file to a patch PNG image with embedded metadata.
    
    Args:
        file_path: Path to the file to encode
        folder_path: Target folder in bot root (e.g., 'lib/utils', 'reactionMemes')
        output_image: Path to save the PNG image (defaults to file_name.patch.png)
    
    Returns:
        Path to the generated patch image
    """
    
    # Read file as bytes
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path_obj, 'rb') as f:
        file_data = f.read()
    
    # Create header: n_<filename>-p_<folder_path>
    filename = file_path_obj.name
    header = f"n_{filename}-p_{folder_path}"
    header_bytes = header.encode('utf-8')
    
    # Combine header + delimiter + file data
    delimiter = b'\x00'
    full_data = header_bytes + delimiter + file_data
    
    # Determine output path
    if output_image is None:
        output_image = str(file_path_obj.with_name(f"{file_path_obj.stem}.patch.png"))
    
    # Calculate image dimensions
    # Each pixel holds 3 bytes (RGB), so we need ceil(len(data) / 3) pixels
    num_pixels = math.ceil(len(full_data) / 3)
    # Use a square-ish layout: width ≈ height
    width = math.ceil(math.sqrt(num_pixels))
    height = math.ceil(num_pixels / width)
    
    # Pad data to fill all pixels (RGB values)
    total_bytes_needed = width * height * 3
    data_padded = full_data + bytes([0] * (total_bytes_needed - len(full_data)))
    
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
    
    # Add metadata to PNG
    from PIL.PngImagePlugin import PngInfo
    pnginfo = PngInfo()
    pnginfo.add_text("patch_filename", filename)
    pnginfo.add_text("patch_folder", folder_path)
    pnginfo.add_text("patch_data_size", str(len(file_data)))
    pnginfo.add_text("patch_header_size", str(len(header_bytes) + 1))  # +1 for delimiter
    image.save(output_image, pnginfo=pnginfo)
    
    print(f"✓ Created patch {output_image}")
    print(f"  File: {filename}")
    print(f"  Target folder: {folder_path}")
    print(f"  File size: {len(file_data)} bytes")
    print(f"  Dimensions: {width}x{height} pixels")
    
    return output_image


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python patch_to_img.py <file> <folder_path> [output.png]")
        print("Example: python patch_to_img.py helper.py lib/utils")
        print("Example: python patch_to_img.py config.json reactionMemes custom_patch.png")
        sys.exit(1)
    
    file_path = sys.argv[1]
    folder_path = sys.argv[2]
    output_image = sys.argv[3] if len(sys.argv) > 3 else None
    
    file_to_patch_image(file_path, folder_path, output_image)
