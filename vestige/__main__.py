from tqdm import tqdm
from comment_parser import comment_parser
from argparse import ArgumentParser
import transformers
from text_classifier import TextClassifier
from glob import iglob

import numpy as np
import os
import logging

from .download_utils import download_url
from .constants import LOCAL_MODEL_NAME, EXTERNAL_MODEL_PATH


logger = logging.getLogger(__name__)
transformers.logging. set_verbosity_warning()

def fix_inline_comments(file_path, tc):
    """Remove commented code while leaving useful comments in-tact.

    Args:
        file_path (str): Path to a python file to clean
        tc (TextClassifier): TextClassifier object that is used to remove comments

    Returns:
        list: Contents of file after cleaning, list of str lines
    """
    assert file_path[-3:] == '.py', "Only python files are currently supported"

    # Read in data for cleaning
    with open(file_path, 'r') as fh:
        read_data = fh.read().split('\n')

    # Extract comments from python files only
    comments = comment_parser.extract_comments(file_path, mime='text/x-python')
    comments = [comment for comment in comments if not comment.is_multiline()]
    removal_indexes = []
    for comment in tqdm(comments):
        # If the model thinks it is commented code
        if np.argmax(tc.predict(str(comment)).cpu(), axis=1) == 1:
            line_num = comment.line_number() - 1
            # -1 to get the '#' as well
            end_index = (len(read_data[line_num]) - len(str(comment))) - 1 

            # Remove it
            line_with_comment_removed = read_data[line_num][0:end_index]
            if len(line_with_comment_removed.strip()) == 0:
                removal_indexes.append(line_num)
            read_data[line_num] = line_with_comment_removed
    
    # We need to remove them from highest index to lowest index so that we don't change the indexing while processing
    removal_indexes.reverse()
    
    # Removes blank lines that were previously comments
    for idx in removal_indexes:
        read_data.pop(idx)
    
    return read_data

def fix_text_lines(file_path, output_path, tc):
    """Removes lines that are most likely commented code from text file

    Args:
        file_path (str): path to input file
        output_path (str): path to output file
        tc (TextClassifier): TextClassifier object to use for prediction
    """
    with open(file_path, 'r') as reader:
        with open(output_path, 'w') as writer:
            for line in tqdm(reader.readlines()):
                if np.argmax(tc.predict(line).cpu(), axis=1) == 0:
                    writer.write(line)
                else:
                    print(f'\n\t"{line}"\n')
                    if input("Is this commented code? y/n :").lower().strip() != 'y':
                        os.system("clear")
                        print("Comment will be left in, thanks!")
                        writer.write(line)

def clean_file(inp, tc, output=None):
    """Remove commented code from the file and write it to disk

    Args:
        input (str): Input file to clean with the textcleaner
        tc (TextCleaner): TextCleaner object to perform cleaning
        output (str, optional): Path to save the cleaned file out to. If none it will overwrite the original file. Defaults to None.
    """
    fixed_lines = fix_inline_comments(inp, tc)
    with open(output, 'w') as fh:
        for i, line in tqdm(enumerate(fixed_lines)):
            if i == 0:
                fh.write(f"{line}")
            else:
                fh.write(f"\n{line}")

def clean_directory(input_folder, tc, output_folder=None):
    """Cleans all python files found in the given directory

    Args:
        input_folder (str): path to the folder to find files under for cleaning
        output_folder (str, optional): Second folder to save out results to. If None, will overwrite files in the given directory. Defaults to None.
    """
    if input_folder[-1] != '/':
        input_folder = input_folder+'/'
    if output_folder is None:
        output_folder = input_folder
    for path in iglob(os.path.join(input_folder, '*.py')):
        sub_path = path.replace(input_folder, '')
        new_path = os.path.join(output_folder, sub_path)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        logging.debug(f"Running with args {path} {new_path}")
        clean_file(path, tc, output=new_path)

if __name__ == '__main__':
    dirname = os.path.dirname(__file__)
    download_path = os.path.join(dirname, LOCAL_MODEL_NAME)
    if not os.path.exists(download_path):
        print("First run, downloading model")
        download_url(EXTERNAL_MODEL_PATH, download_path)
        


    parser = ArgumentParser(description='Remove vestigial comments from code')
    parser.add_argument(
        "input",
        type=str,
        metavar="INPUT_PATH",
        help="Input file or folder for cleaning",
    )
    parser.add_argument('--recursive', '-r', action='store_true', default=False, help='Recursively search a folder and clean files underneat it')
    parser.add_argument('--output', '-o', type=str, default=None, required=False,
                        help='Location to save file/files out to. If using --recursive should be a directory')
    args = parser.parse_args()
    
    if args.output is None:
        output = args.input
    else:
        output = args.output

    tc = TextClassifier()
    tc.load(download_path)
    
    if args.recursive:
        clean_directory(args.input, tc, output_folder=args.output)

    elif args.input[-3:] == '.py':
        clean_file(args.input, tc, output)
    elif args.input[-4:] == '.txt':
        fix_text_lines(args.input, args.output, tc)
    else:
        print("File type unsupported, exiting")
