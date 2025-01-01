import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Any
from openpyxl import load_workbook
import plotly.express as px
from pathlib import Path



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

@st.cache_data()
def read_data(file_path: str) -> (Dict[str, pd.DataFrame], List[str]):

    def load_sheets(file_path: str, sheet_names: List[str], header: int = 3) -> Dict[str, pd.DataFrame]:
        return {name: pd.read_excel(file_path, sheet_name=name, header=header) for name in sheet_names}
    
    sheet_names = pd.ExcelFile(file_path).sheet_names
    sheet_data = load_sheets(file_path, sheet_names[3:7])
    return sheet_data, sheet_names

def build_data_frames():

    path = Path(__file__).parent / "data/raw_data/Zensus22_Sonderauswertung_Haas.xlsx"
    
    #'data/'
    

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


def main():

    dataframes = build_data_frames()
    # Streamlit app
    st.title('Berufe im Zensus 2022 nach Standardklassifikation der Berufe(ISCO-08)')

    def display_markdown(file_name: str):
        # Resolve the full path of the Markdown file relative to the script's directory
        file_path = Path(__file__).parent / "assets/md_text" / file_name
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        st.markdown(content)

    # Example usage
    display_markdown("explain_isco08.md")

    # Select dataframe
    selected_df_name = st.selectbox('Wähle ein Berufsstufe nach dem ISCO-08 aus?', list(dataframes.keys()))
    selected_df = dataframes[selected_df_name]


    # Select number of items
    num_items = st.slider('Select Number of Items', min_value=1, max_value=100, value=10)

    # Display sorted dataframe
    sorted_df = selected_df.sort_values(by='percent', ascending=False).head(num_items)
    st.write(f'Top {num_items} items in percent of {selected_df_name}')

    st.dataframe(sorted_df)

if __name__ == "__main__":
    dataframes = build_data_frames()
    main()