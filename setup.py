"""Setup configuration for ImgExecutor package."""

from setuptools import setup, find_packages

setup(
    name="imgexecutor",
    version="1.0.0",
    description="Execute Python code encoded as PNG images",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "imgexecutor=imgexecutor:image_to_python",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
