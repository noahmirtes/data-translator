# main.py

from templates import extract_template_structure
from utils import read_excel_sheet, export_data, construct_output_df, construct_output_filename
from post_process import copy_by_header, run_post_processes

# ------------------------------------------ #

def main(input_path : str, output_folder : str, template_path : str, template_name : str):

    # load the data template
    DATA_TEMPLATE = extract_template_structure(template_path, template_name)

    # init the input and output dataframes
    input_df = read_excel_sheet(input_path)
    output_df = construct_output_df(headers=DATA_TEMPLATE.header_map.keys())

    # do 1:1 mapping
    output_df = copy_by_header(
        src_df=input_df,
        dest_df=output_df,
        header_map=DATA_TEMPLATE.header_map
    )
    
    # run the post processing
    output_df = run_post_processes(
        df=output_df,
        transforms=DATA_TEMPLATE.post_processes
    )

    # construct the output path
    output_path = construct_output_filename(
        input_path=input_path,
        output_folder=output_folder,
        template_name=template_name
    )

    # export the data
    export_data(
        output_path=output_path,
        df=output_df
    )


# ------------------------------------------ #

if __name__ == "__main__":
    # TEST HARNESS #
    main(
        input_path="/Users/noah/REPOS/basic-data-translator/examples/input/harvest_input.xlsx",
        output_path="/Users/noah/REPOS/basic-data-translator/examples/output",
        template_path="/Users/noah/REPOS/basic-data-translator/TEMPLATES.json",
        template_name="harvest_to_sourceaudio"
    )
