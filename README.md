# ImgExecutor

Execute Python code encoded as PNG images. Convert your scripts to pixel art and run them back as Python!

## How it works

1. **py_to_img.py** - Converts Python files to PNG images
   - Reads your `.py` file as binary data
   - Encodes each 3 bytes as RGB pixel values
   - Generates a square-ish PNG image
   - Stores metadata (original file size and name)

2. **imgexecutor** - Decodes PNG images back to Python and executes them
   - Reads PNG pixel data
   - Decodes RGB values back to binary
   - Reconstructs the original Python source
   - Can execute the decoded code directly

3. **gui.py** - PyQt5 GUI application
   - Browse and select PNG images
   - View decoded Python code
   - Execute with output in terminal emulator
   - Dark theme for comfort

## Usage

### Python → Image
```bash
python "py to img.py" script.py
# Creates: script.png
```

### Image → Python (CLI)
```bash
python -m imgexecutor script.png
# Creates: script.py
```

### Image → Python (execute immediately)
```bash
python -m imgexecutor script.png --execute
# Runs the code directly
```

### GUI Application
```bash
python gui.py
```
Then:
1. Click "📁 Browse PNG" to select an image
2. View decoded code on the left
3. Click "▶ Run Image as Python" to execute

## Example Workflow

```bash
# 1. Convert example.py to image
python "py to img.py" example.py

# 2. Run it via CLI
python -m imgexecutor example.png --execute

# 3. Or use the GUI
python gui.py
```

## Technical Details

- **Encoding**: Binary data → RGB pixel values (3 bytes per pixel)
- **Image Format**: PNG (lossless, preserves exact data)
- **Data Preservation**: Original file size stored in PNG metadata
- **Execution**: Uses Python's `exec()` to run decoded code
- **Character Encoding**: UTF-8 with fallback to Latin-1

## Installation (Optional)

```bash
pip install -e .
```

Then use:
```bash
imgexecutor script.png --execute
```

## Limitations

- The encoded image won't look like much (essentially random colored pixels)
- File size increases slightly due to PNG encoding overhead
- The entire file must fit in memory during encoding/decoding
- Very large Python files may create large image files

## Why this is cool 🚀

- 🎨 **Obfuscation**: Your Python code is hidden in an image
- 🖼️ **Artistic**: Logic encoded as pixels
- 🔬 **Experimental**: Unconventional program distribution
- 🎭 **Fun**: A neat proof-of-concept!

