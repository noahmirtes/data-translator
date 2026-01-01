# cli.py

import argparse
from main import main

parser = argparse.ArgumentParser(description="A CLI version of the basic data translator")

parser.add_argument("name", help="The name of the user to greet.")

parser.add_argument("--input_path", action="store_true", help="Path to the input data file")
parser.add_argument("--output_path", action="store_true", help="Path to the output data file")
parser.add_argument("--template_path", action="store_true", help="Path to the json template file")
parser.add_argument("--template_name", action="store_true", help="Name of the template to be used")

# 4. Parse the arguments from the command line
args = parser.parse_args()

main(
    input_path=args.input_path,
    output_path=args.output_path,
    template_path=args.template_path,
    template_name=args.template_name
)