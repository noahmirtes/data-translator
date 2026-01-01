# utils.py

import os
import pandas as pd

# ------------------------------------------ #
# data IO

def read_excel_sheet(path : str) -> pd.DataFrame:
    return pd.read_excel(path, dtype='str')


def export_data(output_path : str, df : pd.DataFrame):
    """
    Exports the dataframe to the path specified in the correct format
    Automatically selects the right save function based on the path extension
    
    Args:
        output_path : path to the data export
        df : the dataframe to be exported
    """
    ext = os.path.splitext(output_path)[-1]

    if ext == '.csv':
        df.to_csv(output_path, index=False)
    elif ext == '.xlsx':
        df.to_excel(output_path, index=False)
    elif ext == '.txt':
        df.to_csv(output_path, sep='\t', index=False)
    else:
        print(f"Output extension {ext} not supported.")
        
def construct_output_df(headers : list[str]):
    """
    Construct a blank dataframe with the headers specified
    Note that the order of the headers in the list will be the order of the columns in the df

    Args:
        Headers : a list of headers
    """
    return pd.DataFrame(columns=headers)

# ------------------------------------------ #
# Data tools

def split_tag_list(raw, delimiter=';'):
    """Split a cell into a list of tags. Always assumes semicolon delimiter"""
    
    if pd.isna(raw):
        return []
    
    s = str(raw).strip()
    if not s:
        return []

    parts = [p.strip() for p in s.split(delimiter)]

    return [p for p in parts if p]
