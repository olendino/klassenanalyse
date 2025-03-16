import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Any
from openpyxl import load_workbook
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from pathlib import Path

#how the side appears in the browser
st.set_page_config(page_title="Klassenanalyse",layout="wide")


def set_up_data():
    # Get the directory where the script is located
    base_path = Path(__file__).parent
    
    # Define relative paths from the script location
    path_digiclass = base_path / "data/processed_data/added_digiclass.csv"
    digiclass_data = pd.read_csv(path_digiclass, index_col=0)
    
    path_livingstone = base_path / "data/processed_data/isco_livingstone.csv"
    livingstone_data = pd.read_csv(path_livingstone, index_col=0)  # Fixed: now loads livingstone data
    
    # Merge the datasets
    merged_data = pd.merge(digiclass_data, livingstone_data, left_on='ISCO.Code', right_on='ISCO-Code')
    merged_data.drop(columns=['ISCO.Code'], inplace=True)
    
    return merged_data


livingstone_data = set_up_data()

# Only update the rows where Stellung.im.Beruf has specific values
# Change 'Selbstständige ohne Beschäftigte' to 'Selbstständige'
livingstone_data.loc[livingstone_data['Stellung.im.Beruf'] == 'Selbstständige ohne Beschäftigte', 'modifiziert_livingstone'] = 'Selbstständige'

# Keep 'Selbstständige mit Beschäftigten' as is 
# (this line isn't necessary if you don't need to change it, but included for clarity)
livingstone_data.loc[livingstone_data['Stellung.im.Beruf'] == 'Selbstständige mit Beschäftigten', 'modifiziert_livingstone'] = 'Selbstständige mit Beschäftigten'

# TODO fix nans (Offiziere)
livingstone_data_clean = livingstone_data.dropna(subset=["modifiziert_livingstone"])

# Calculate percentages for each class (aggregating by modifiziert_livingstone)
class_totals = livingstone_data.groupby('modifiziert_livingstone')['Anzahl'].sum().reset_index()
total_sum = class_totals['Anzahl'].sum()
class_totals['Percent'] = (class_totals['Anzahl'] / total_sum * 100).round(1)

# Merge the percentages back to the main dataframe
livingstone_data = pd.merge(
    livingstone_data, 
    class_totals[['modifiziert_livingstone', 'Percent']], 
    on='modifiziert_livingstone', 
    how='left'
)

# Define the specific order you want
fraktion_order = [
    "Selbstständige", 
    "Selbstständige mit Beschäftigten",  # Besitzer
    "Top Management", 
    "Mittleres Management", 
    "Anleitende Beschäftigte",  # Manager
    "Hochspezialisierte Beschäftigte", 
    "Industriearbeiter*innen", 
    "Dienstleistungsarbeiter*innen"  # Arbeiter*innenklasse
]

colors = [
    '#1D4E1F',  # Dark green - Military (distinct from the others)
    '#0A1F44',  # Dark navy blue - Managers (more distinct from the others)
    '#F5B461',  # Golden yellow - Professionals (brighter)
    '#00CED1',  # DarkTurquoise - Technicians (brighter for distinction)
    '#9B59B6',  # Medium purple - Clerical (distinct from light purple)
    '#FF6B6B',  # Coral red - Service workers
    '#4A90E2',  # Sky blue - Agricultural
    '#af005f',  # deep pink - Craft workers
    '#4B2F2F',  # dark brown - Plant operators (more distinct from yellow)
    '#F2C9B3'   # Soft peach - Elementary (lighter for distinction)
]



# Create the bar chart with the custom order
fig = px.bar(
    livingstone_data,
    x="Anzahl",
    y="modifiziert_livingstone",
    color='major_group',
    orientation='h',
    hover_data={
        'Berufsgattung(ISCO-Stufe 4)': True,
        'Anzahl': True,
        'modifiziert_livingstone': False,
        'major_group': False
    },
    title='Klassenanalyse',
    color_discrete_sequence=colors,
    category_orders={"modifiziert_livingstone": fraktion_order}
)
# Style the silces of the bars with black borders and slight transparency
fig.update_traces(
    marker=dict(line=dict(width=0.5, color='black')),
    opacity=0.8
)

# Add percentage annotations for each class
for i, klasse in enumerate(fraktion_order):
    if klasse in class_totals['modifiziert_livingstone'].values:
        percent_value = class_totals.loc[class_totals['modifiziert_livingstone'] == klasse, 'Percent'].values[0]
        count_value = class_totals.loc[class_totals['modifiziert_livingstone'] == klasse, 'Anzahl'].values[0]
        
        # Add annotation for the percentage, positioned far to the right
        fig.add_annotation(
            x=count_value * 1.005,  # Multiply by a factor to move further right
            y=klasse,
            text=f"{percent_value}%",
            showarrow=False,
            font=dict(size=12, color="white"),
            align="left"
        )

# Update layout
fig.update_layout(
    autosize=True,
    height=750,
    #width=1400,
    legend=dict(
        title="Hauptgruppen ISCO-Stufe 1",
        font=dict(size=12),
        orientation="v",  # vertical orientation
        yanchor="top",    # anchor point at the top of the legend
        y=0.5,              # position at the top of the chart (y=0.5)
        xanchor="right",  # anchor point at the right of the legend
        x=1,              # position at the right of the chart (x=1)
        
    ),
    yaxis={
            'categoryorder': 'array',
            'categoryarray': fraktion_order[::],
            'title': 'Klassenfraktionen',  # Add a title for the y-axis
            'title_standoff': 25,  # Distance between the axis and its title
            'tickfont': {'size': 14,'weight':'bold'},  # Font size for the tick labels
            'titlefont': {'size': 14, 'color': 'white'}  # Font for the axis title
    },
    margin=dict(l=200),  # Increased right margin for meta-category labels
    
)

st.write("# Klassen in Deutschland eine Datenanalyse")

st.write("Moin seit Jahren nervt mich die Frage Wer ist eigentlich die Arbeiter*innenklasse in einer modernen Gesellellschaft."
"Das ist mein bescheidner Versuch dazu einen Beitrag zu leisten."
" **Ein großteil der Kategorien und Überlegungen gehen auf den Soziologen D.W. Livingstone zurück. Die Datenbasieren auf dem Zensus 2022 und den darin enthaltenen ISCO-08 Codes**")

st.plotly_chart(fig,use_container_width=True)







