"""
Extract a file from a patch PNG image.
Decodes header and file data from embedded metadata and pixel data.
"""

import sys
from pathlib import Path
from PIL import Image


def patch_image_to_file(image_file: str, output_file: str = None, target_folder: str = None) -> dict:
    """
    Extract a file from a patch PNG image.
    
    Args:
        image_file: Path to the patch PNG image
        output_file: Path to save the extracted file (overrides patch metadata)
        target_folder: Optional override for target folder
    
    Returns:
        Dictionary with keys: filename, folder, file_path, data_size
    """
    
    # Open image
    image_path = Path(image_file)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_file}")
    
    image = Image.open(image_path)
    
    # Extract RGB pixel data
    pixels = list(image.getdata())
    
    # Convert RGB tuples back to bytes
    data_bytes = bytearray()
    for r, g, b in pixels:
        data_bytes.append(r)
        data_bytes.append(g)
        data_bytes.append(b)
    
    # Remove trailing null bytes
    while data_bytes and data_bytes[-1] == 0:
        data_bytes.pop()
    
    # Find delimiter (null byte)
    delimiter_index = data_bytes.find(b'\x00')
    if delimiter_index == -1:
        raise ValueError("No header delimiter found in patch image")
    
    # Extract header and file data
    header_bytes = bytes(data_bytes[:delimiter_index])
    file_data = bytes(data_bytes[delimiter_index + 1:])
    
    # Parse header: n_<filename>-p_<folder_path>
    try:
        header_str = header_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError(f"Could not decode header as UTF-8")
    
    # Parse header format: n_<filename>-p_<folder_path>
    parts = header_str.split('-p_')
    if len(parts) != 2:
        raise ValueError(f"Invalid patch header format: {header_str}")
    
    filename_part = parts[0]
    folder_path = parts[1]
    
    if not filename_part.startswith('n_'):
        raise ValueError(f"Invalid filename prefix in header: {filename_part}")
    
    filename = filename_part[2:]  # Remove 'n_' prefix
    
    # Determine output path
    if output_file:
        output_path = Path(output_file)
    elif target_folder:
        output_path = Path(target_folder) / filename
    else:
        output_path = Path(filename)
    
    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(output_path, 'wb') as f:
        f.write(file_data)
    
    result = {
        'filename': filename,
        'folder': folder_path,
        'file_path': str(output_path),
        'data_size': len(file_data)
    }
    
    print(f"✓ Extracted patch from {image_file}")
    print(f"  Filename: {filename}")
    print(f"  Target folder: {folder_path}")
    print(f"  Saved to: {output_path}")
    print(f"  File size: {len(file_data)} bytes")
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python img_to_patch.py <patch.png> [output_file] [--folder target_folder]")
        print("Example: python img_to_patch.py helper.patch.png")
        print("Example: python img_to_patch.py patch.png custom_name.py")
        print("Example: python img_to_patch.py patch.png --folder lib/utils")
        sys.exit(1)
    
    image_file = sys.argv[1]
    output_file = None
    target_folder = None
    
    # Parse optional arguments
    if len(sys.argv) > 2:
        if sys.argv[2] == '--folder' and len(sys.argv) > 3:
            target_folder = sys.argv[3]
        else:
            output_file = sys.argv[2]
            if len(sys.argv) > 3 and sys.argv[3] == '--folder' and len(sys.argv) > 4:
                target_folder = sys.argv[4]
    
    patch_image_to_file(image_file, output_file, target_folder)
