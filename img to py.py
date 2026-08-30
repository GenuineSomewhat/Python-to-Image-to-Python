"""
Convert PNG images back to Python source files and optionally execute them.
Decodes RGB pixel values back to binary data.
"""

import sys
from pathlib import Path
from PIL import Image


def image_to_python(image_file: str, output_python: str = None, execute: bool = False) -> str:
    """
    Convert a PNG image back to Python source code.
    
    Args:
        image_file: Path to the PNG image
        output_python: Path to save the .py file (defaults to image_file.py)
        execute: Whether to execute the decoded Python code
    
    Returns:
        The decoded Python source code
    """
    
    # Open image
    image_path = Path(image_file)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_file}")
    
    image = Image.open(image_path)
    
    # Get metadata to find original data size
    metadata = image.info.get('pnginfo', None)
    original_size = None
    
    if hasattr(image, 'info'):
        original_size_str = image.info.get('original_size', None)
        if original_size_str:
            try:
                original_size = int(original_size_str)
            except ValueError:
                pass
    
    # Extract RGB pixel data
    pixels = list(image.getdata())
    
    # Convert RGB tuples back to bytes
    data_bytes = bytearray()
    for r, g, b in pixels:
        data_bytes.append(r)
        data_bytes.append(g)
        data_bytes.append(b)
    
    # Trim to original size if metadata available
    if original_size:
        data_bytes = data_bytes[:original_size]
    else:
        # Remove trailing null bytes
        while data_bytes and data_bytes[-1] == 0:
            data_bytes.pop()
    
    # Decode to string
    try:
        source_code = data_bytes.decode('utf-8')
    except UnicodeDecodeError:
        print("Warning: Could not decode as UTF-8, trying with latin-1")
        source_code = data_bytes.decode('latin-1')
    
    # Save to output file if specified
    if output_python:
        output_path = Path(output_python)
    else:
        output_path = image_path.with_suffix('.py')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(source_code)
    
    print(f"✓ Converted {image_file} → {output_path}")
    print(f"  Decoded {len(source_code)} characters")
    
    # Execute if requested
    if execute:
        print("\n--- Executing decoded Python code ---")
        try:
            exec(source_code, {'__file__': str(output_path)})
            print("--- Execution completed ---\n")
        except Exception as e:
            print(f"--- Error during execution ---")
            print(f"Error: {e}")
            print("--- Execution failed ---\n")
            raise
    
    return source_code


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python img_to_py.py <image.png> [output.py] [--execute]")
        print("Example: python img_to_py.py script.png")
        print("Example: python img_to_py.py script.png decoded.py --execute")
        sys.exit(1)
    
    image_file = sys.argv[1]
    output_python = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    execute_flag = '--execute' in sys.argv
    
    image_to_python(image_file, output_python, execute_flag)
