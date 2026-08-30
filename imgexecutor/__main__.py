"""
Command-line interface for imgexecutor package.
Usage: python -m imgexecutor <image.png> [output.py] [--execute]
"""

import sys
from . import image_to_python


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m imgexecutor <image.png> [output.py] [--execute]")
        print("Example: python -m imgexecutor script.png")
        print("Example: python -m imgexecutor script.png decoded.py --execute")
        sys.exit(1)
    
    image_file = sys.argv[1]
    output_python = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    execute_flag = '--execute' in sys.argv
    
    image_to_python(image_file, output_python, execute_flag)


if __name__ == "__main__":
    main()
