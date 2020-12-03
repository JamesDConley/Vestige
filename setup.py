import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vestige-cleaner",
    version="0.0.1a1",
    author="James Conley",
    author_email="jconley1+vestige@alumni.conncoll.edu",
    description="Remove commented code from projects automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JamesDConley/Vestige",
    packages=setuptools.find_packages(),
    install_requires=['bert-text-classifier', 'tqdm', 'comment_parser', 'argparse', 'numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
