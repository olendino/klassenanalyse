import pandas as pd

def missing_values_col_isco_bezeichnung(df):
    df["ISCO-Code"] = df["ISCO-Code"].ffill()
    df["Bezeichnung"] = df["Bezeichnung"].ffill()
    return df



def clean_col_insgesamt_to_anzahl(df):
    df = df.replace('/', '0')
    # Extract rows where 'Anzahl' is not a number using regex
    non_numeric_rows = df[~df['Insgesamt'].astype(str).str.match(r'^\d+$')]
    print(non_numeric_rows)

    #drop rows which have duplicated information
    # from col Stellung im Beruf to Insgesamt
    df = df[df["Stellung im Beruf"] != "Insgesamt"]

    #finally rename the column and return
    df.rename(columns={'Insgesamt':'Anzahl'},inplace=True)
    return df

def build_additional_columns(df):
    #build is_supervisor column:
    df = df.assign(is_supervisor=0)
    df['is_supervisor'] = df['ISCO-Code'].apply(lambda x: 1 if str(x).startswith('1') else 0)

    #NUMBER OF EMPLOYEES
    df = df.assign(n_employees=0)
    df.loc[df['Stellung im Beruf'] == "Selbstständige mit Beschäftigten", 'n_employees'] = 5

    #SELF_EMPLOYEED
    df = df.assign(self_employed=0)
    df.loc[(df['Stellung im Beruf'] == "Selbstständige mit Beschäftigten") | (df['Stellung im Beruf'] == "Selbstständige ohne Beschäftigte"), 'self_employed'] = 1

    df=df.assign(control_work=4)
    df=df.assign(control_daily=2)

    return df

def transform_employment_data(df):
    """
    Transform employment data by:
    1. Identifying self-employed and non-self-employed workers
    2. Grouping non-self-employed workers by ISCO-Code
    3. Summing the count columns for each ISCO-Code group
    4. Adding a new category name column for non-self-employed
    5. Combining the transformed non-self-employed data with the original self-employed data
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing employment data with 'Stellung im Beruf' and 'ISCO-Code' columns
    
    Returns:
    pandas.DataFrame: Combined DataFrame with non-self-employed categories grouped and original self-employed rows
    """
    # Define the self-employed categories
    self_employed_categories = [
        'Selbstständige mit Beschäftigten',
        'Selbstständige ohne Beschäftigte'
    ]
    
    # Define the state columns and Anzahl
    all_count_columns = [
        'Anzahl', 'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg',
        'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern',
        'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz',
        'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein',
        'Thüringen'
    ]
    
    # Create a filter mask for self-employed workers
    filter_mask = df['Stellung im Beruf'].isin(self_employed_categories)
    
    # Extract self-employed rows
    self_employed_df = df[filter_mask]
    
    # Group by ISCO-Code and sum all columns that have a count for the group for non-self-employed workers
    non_self_employed_sum = df[~filter_mask].groupby('ISCO-Code')[all_count_columns].sum().reset_index()
    
    # Add a new category name column
    non_self_employed_sum['category'] = 'Arbeiter*innen & Angestellte'
    
    # Combine the two DataFrames
    prep_df = pd.concat([non_self_employed_sum, self_employed_df])
    
    return prep_df

def remove_header_rows(df):
    """Remove the first 7 rows of the dataframe"""
    return df.drop(df.index[:7])


def main():
    file_path ='/Users/leonardhaas/code/streamlit/data/raw_data/Zensus2022_Erwerbstaetige.xlsx'

    df = pd.read_excel(file_path, sheet_name="Daten", skiprows=2)

    #rename columns:

    df.rename(columns={
        df.columns[0]: "ISCO-Code",
        df.columns[1]: "Bezeichnung",
        df.columns[2]: "Stellung im Beruf",
        df.columns[3]: "Insgesamt"
    }, inplace=True)

    df.rename(columns={
    "Name Bundesland zum Zensusstichtag (15.05.2022)": 'Baden-Württemberg',
    'Unnamed: 5': 'Bayern',
    'Unnamed: 6': 'Berlin',
    'Unnamed: 7': 'Brandenburg',
    'Unnamed: 8': 'Bremen',
    'Unnamed: 9': 'Hamburg',
    'Unnamed: 10': 'Hessen',
    'Unnamed: 11': 'Mecklenburg-Vorpommern',
    'Unnamed: 12': 'Niedersachsen',
    'Unnamed: 13': 'Nordrhein-Westfalen',
    'Unnamed: 14': 'Rheinland-Pfalz',
    'Unnamed: 15': 'Saarland',
    'Unnamed: 16': 'Sachsen',
    'Unnamed: 17': 'Sachsen-Anhalt',
    'Unnamed: 18': 'Schleswig-Holstein',
    'Unnamed: 19': 'Thüringen'
    }, inplace=True)

    # fills the empty rows from human readable to machine readable 
    df = missing_values_col_isco_bezeichnung(df)

    df = clean_col_insgesamt_to_anzahl(df)
    print(df.dtypes)

    df = build_additional_columns(df)
    print(df.dtypes)

    df = df.drop(df.index[:7])

    # Define the columns and their new data types
    columns_to_convert = {
        'Anzahl': 'int64',
        'Baden-Württemberg': 'int64',
        'Bayern': 'int64',
        'Berlin': 'int64',
        'Brandenburg': 'int64',
        'Bremen': 'int64',
        'Hamburg': 'int64',
        'Hessen': 'int64',
        'Mecklenburg-Vorpommern': 'int64',
        'Niedersachsen': 'int64',
        'Nordrhein-Westfalen': 'int64',
        'Rheinland-Pfalz': 'int64',
        'Saarland': 'int64',
        'Sachsen': 'int64',
        'Sachsen-Anhalt': 'int64',
        'Schleswig-Holstein': 'int64',
        'Thüringen': 'int64'
    }

    df = df.astype(columns_to_convert)
    
    #make test caluclation for 5 ISCO groups if sum is right -> DONE see check_calculation.md
    df = transform_employment_data(df)
    
    df = remove_header_rows(df)

    #this should come last
    df = build_additional_columns(df)
    
    # Save the cleaned data
    df.to_csv('/Users/leonardhaas/code/streamlit/data/processed_data/test_digiclass04.csv', index=False)
 
    #print(df.dtypes)

if __name__ == "__main__":
    main()