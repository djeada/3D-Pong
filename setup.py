from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="3D_Pong",
    version="0.1.0",
    author="Your Name",
    author_email="addjellouli1@gmail.com",
    description="A 3D implementation of the classic game Pong using the Visualization Toolkit (VTK).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djeada/3D-Pong",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "vtk",
    ],
    entry_points={
        'console_scripts': [
            '3d_pong=main:main',
        ],
    },
)
