# Vestige

Vestige is a tool that automatically finds and removes commented code from python files.

For example, you can use the tool to remove some comments within an old vestige file, and output the result into another file cleaned.py like this.
```
python -m vestige cleaner.py --output cleaned.py
```

## Usage
You can view the full usage with the --help option
```
python -m vestige --help
```
which yields
```
usage: __main__.py [-h] [--recursive] [--output OUTPUT] INPUT_PATH

Remove vestigial comments from code

positional arguments:
  INPUT_PATH            Input file or folder for cleaning

optional arguments:
  -h, --help            show this help message and exit
  --recursive, -r       Recursively search a folder and clean files underneat it
  --output OUTPUT, -o OUTPUT
                        Location to save file/files out to. If using --recursive should be a directory
```

## Installation

To install with pip
```
pip install vestige-cleaner
```

## Q/A
- Will vestige break my code!?

Thankfully, no! Vestige only analyzes inline comments, so while it's possible for it to remove some inline documentation by mistake, it won't ever affect the actual code.
- How much can I trust vestige?

Vestige's current model is about 95% accurate on internal tests.  We recommend double checking the diff of the original and output files to ensure everything has worked properly.  In the future we are aiming to increase this accuracy significantly through improvement of both the model and the training dataset.

- How does vestige work?

Vestige uses [BERT](https://arxiv.org/abs/1810.04805), a transformer based artificial neural network that is pretrained to better *understand (kind of)* language, and then fine tuned on a specific task.  In this case, it is fine tuned to distinguish between commented code and useful documentation.