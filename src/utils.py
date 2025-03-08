import pandas as pd
import streamlit as st
from pathlib import Path
from openpyxl import load_workbook
from typing import List, Dict, Optional, Any




def clean_group(df: pd.DataFrame,bundesländer_cols:list) -> pd.DataFrame:
   # Replace '/' with '0' and convert 'Insgesamt' column to integer
   df = df.replace('/', '0')
   df['Insgesamt'] = df['Insgesamt'].astype(int)
   
   # Calculate the total and percentage
   total = df['Insgesamt'].iloc[0]
   df['percent'] = (df['Insgesamt'] / total) * 100
   
   # Drop unnecessary columns and the first row
   df = df.drop(columns=bundesländer_cols)
   df = df.drop(index=0)
   
   return df

#@st.cache_data()
def read_data(file_path: str) -> (Dict[str, pd.DataFrame], List[str]):

    def load_sheets(file_path: str, sheet_names: List[str], header: int = 3) -> Dict[str, pd.DataFrame]:
        return {name: pd.read_excel(file_path, sheet_name=name, header=header) for name in sheet_names}
    
    sheet_names = pd.ExcelFile(file_path).sheet_names
    sheet_data = load_sheets(file_path, sheet_names[3:7])
    return sheet_data, sheet_names

def build_data_frames():
    BASE_DIR = Path.cwd().parent


    # Construct the path to your Excel file
    path = BASE_DIR / "data" / "raw_data" / "Zensus22_Sonderauswertung_Haas.xlsx"
    print(path)

    sheet_data,sheet_names = read_data(path)   
    haupt_gruppen_1 = sheet_data[sheet_names[3]]
    berufs_gruppen_2 = sheet_data[sheet_names[4]]
    berufs_unter_gruppen_3 = sheet_data[sheet_names[5]]
    berufs_gattungen_4 = sheet_data[sheet_names[6]]


    bundesländer_cols =['Baden-Württemberg', 'Bayern',
        'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen',
        'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen',
        'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt',
        'Schleswig-Holstein', 'Thüringen']

    haupt_gruppen_1 = clean_group(haupt_gruppen_1, bundesländer_cols)
    berufs_gruppen_2 = clean_group(berufs_gruppen_2, bundesländer_cols)
    berufs_unter_gruppen_3 = clean_group(berufs_unter_gruppen_3, bundesländer_cols)
    berufs_gattungen_4 = clean_group(berufs_gattungen_4, bundesländer_cols)

    dataframes = {
        'Hauptgruppe (1-Str.)': haupt_gruppen_1,
        'Berufsgruppe (2-Str.)': berufs_gruppen_2,
        'Berufsuntergruppen (3-St.)': berufs_unter_gruppen_3,
        'Berufsgattung (4-St.)': berufs_gattungen_4
    }
    return dataframes

def analyze_merge(left_df, right_df, left_on, right_on, how='left'):
    """
    Analyze merge performance between two dataframes.
    
    Parameters:
    -----------
    left_df : pandas.DataFrame
        The first (left) dataframe to merge
    right_df : pandas.DataFrame
        The second (right) dataframe to merge
    left_on : str
        Column name to merge on in the left dataframe
    right_on : str
        Column name to merge on in the right dataframe
    how : str, optional (default='left')
        Type of merge to perform. Options are 'left', 'right', 'inner', 'outer'
    
    Returns:
    --------
    tuple : (merged_dataframe, merge_analysis_report)
    """
    import pandas as pd
    
    # Perform merge with indicator
    merged_data = left_df.merge(
        right_df, 
        left_on=left_on, 
        right_on=right_on, 
        how=how,
        indicator=True
    )
    
    # Analyze merge results
    merge_counts = merged_data['_merge'].value_counts()
    
    # Get unmatched rows from left dataframe
    unmatched_rows = merged_data[merged_data['_merge'] == 'left_only']
    
    # Calculate match statistics
    total_rows = len(left_df)
    total_unique_keys = left_df[left_on].nunique()
    matched_unique_keys = merged_data[merged_data['_merge'] == 'both'][left_on].nunique()
    
    # Calculate match percentage based on unique keys
    match_percentage = (matched_unique_keys / total_unique_keys) * 100 if total_unique_keys > 0 else 0
    
    # Prepare detailed report
    report = {
        'total_rows_left': total_rows,
        'total_unique_keys_left': total_unique_keys,
        'matched_unique_keys': matched_unique_keys,
        'unmatched_unique_keys': total_unique_keys - matched_unique_keys,
        'merged_total_rows': len(merged_data),
        'match_percentage_unique_keys': match_percentage,
        'merge_type': how,
        'merge_counts': merge_counts.to_dict(),
        'unmatched_keys': unmatched_rows[left_on].unique().tolist()
    }
    
    # Print detailed report
    print("Merge Analysis Report:")
    print(f"Total rows in left dataset: {report['total_rows_left']}")
    print(f"Unique keys in left dataset: {report['total_unique_keys_left']}")
    print(f"Matched unique keys: {report['matched_unique_keys']}")
    print(f"Unmatched unique keys: {report['unmatched_unique_keys']}")
    print(f"Total rows in merged dataset: {report['merged_total_rows']}")
    print(f"Match Percentage (unique keys): {report['match_percentage_unique_keys']:.2f}%")
    print("\nMerge Counts:")
    for merge_type, count in report['merge_counts'].items():
        print(f"{merge_type}: {count}")
    
    # Remove the merge indicator column before returning
    merged_data = merged_data.drop(columns=['_merge'])
    
    return merged_data, report