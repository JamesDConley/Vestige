from tqdm import tqdm
from comment_parser import comment_parser
from argparse import ArgumentParser
from text_classifier import TextClassifier
import numpy as np
import os
from download_utils import download_url
from constants import LOCAL_MODEL_PATH, EXTERNAL_MODEL_PATH

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
        # If the model things it is commented code
        if np.argmax(tc.predict(str(comment)).cpu(), axis=1) == 1:
            line_num = comment.line_number() - 1
            end_index = read_data[line_num].index(str(comment)) - 1
            # Remove it
            line_with_comment_removed = read_data[line_num][0:end_index]
            if len(line_with_comment_removed.strip()) == 0:
                removal_indexes.append(line_num)
            read_data[line_num] = line_with_comment_removed
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
                        print("Comment will be left in, thanks!")
                        writer.write(line)


if __name__ == '__main__':
    dirname = os.path.dirname(__file__)
    download_path = os.path.join(dirname, LOCAL_MODEL_PATH)
    if not os.path.exists(download_path):
        print("First run, downloading model")
        download_url(EXTERNAL_MODEL_PATH, download_path)


    parser = ArgumentParser(description='Remove vestigial comments from code')
    parser.add_argument('--input', type=str, required=True,
                        help='Input file for cleaning')
    parser.add_argument('--output', type=str, default=None, required=False,
                        help='sum the integers (default: find the max)')
    tc = TextClassifier()
    tc.load('model_v2.pt')
    args = parser.parse_args()
    if args.input[-3:] == '.py':
        fixed_lines = fix_inline_comments(args.input, tc)
        with open(args.output, 'w') as fh:
            for line in tqdm(fixed_lines):
                fh.write(f"{line}\n")
    else:
        fix_text_lines(args.input, args.output, tc)



    



    

