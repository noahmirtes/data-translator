# main.py

from templates import extract_template_structure
from utils import read_excel_sheet, export_data, construct_output_df
from post_process import copy_by_header, run_post_processes

# ------------------------------------------ #

def main(input_path, output_path, template_path, template_name):

    # load the data template
    DATA_TEMPLATE = extract_template_structure(template_path, template_name)

    # init the input and output dataframes
    input_df = read_excel_sheet(input_path)
    output_df = construct_output_df(columns=DATA_TEMPLATE.header_map.values())

    # do 1:1 mapping
    output_df = copy_by_header(
        src_df=input_df,
        dest_df=output_df,
        header_map=DATA_TEMPLATE.header_map
    )
    
    output_df = run_post_processes(
        df=output_df,
        transforms=DATA_TEMPLATE.post_processes
    )

    export_data(
        output_path=output_path,
        df=output_df
    )


# ------------------------------------------ #

if __name__ == "__main__":
    main(
        input_path="/Users/noah/Library/Mobile Documents/com~apple~CloudDocs/Visual Studio/Data Translator/input_data/input_data.xlsx",
        output_path="/Users/noah/Library/Mobile Documents/com~apple~CloudDocs/Visual Studio/Data Translator/input_data/output_data.xlsx",
        template_path="/Users/noah/Library/Mobile Documents/com~apple~CloudDocs/Visual Studio/Data Translator/TEMPLATES.json",
        template_name="basic_test"
    )
