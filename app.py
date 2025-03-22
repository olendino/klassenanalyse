import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Any
from openpyxl import load_workbook
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from pathlib import Path

#how the side appears in the browser

st.set_page_config(page_title="Klassenanalyse",layout="wide",initial_sidebar_state="collapsed")


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
livingstone_data_clean = livingstone_data.dropna(subset=["modifiziert_livingstone"]) # -> ???

#TODO include meta categories
meta_categories = ["Besitzer", "Management", "Angestellte/Arbeiter*innen"]
subcategories = {
    "Besitzer": ["Selbstständige", "Selbststänige mit Beschäftigten"],
    "Management": ["Anleitende Beschäftigte", "Mittleres Management", "Top Management"],
    "Angestellte/Arbeiter*innen": ["Dienstleistungsarbeiter*innen", "Industriearbeiter*innen","Hochqualifizierte Beschäftigte"]
}


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
    "Selbstständige mit Beschäftigten",  # Besitzer
    "Selbstständige", 
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
    
    title='Klassenanalyse in Anlehnung and Livingstone für Deutschland',
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
    xaxis={
        'title': 'Anzahl der Erwerbtstätigen in Milionen',
        'title_standoff': 10,  # Distance between the axis and its title
        'titlefont': {'size': 14, 'color': 'white'}  # Font for the axis title
    },
    margin=dict(l=200, r=50),  # Increased right margin for meta-category labels
    
    
)
# Add source information at the bottom
fig.add_annotation(
    text="Quelle: Zensus 2022 | Statistisches Bundesamt",
    showarrow=False,
    xref="paper", yref="paper",
    x=-0.001, y=-0.075,
    xanchor="center", yanchor="top",
    font=dict(size=12, color="gray")
)

# Add reading explanation box
fig.add_annotation(
    text="Der Graph zeigt die Anzahl der verschieden Klassenfraktionen auf Basis der Zensus Variablen: Stellung im Beruf und ISCO-08.<br>" +
         "Die Schartierungen des Balken geben die Bestandteile der Fraktionen in Berufsgattungen(ISCO Stufe 4) wieder.<br>" +
         "Die Farben geben die Hauptgruppen (ISCO Stufe 1) wieder",
    showarrow=False,
    xref="paper", yref="paper",
    x=0.4, y=-0.112,
    xanchor="center", yanchor="top",
    bordercolor="lightgrey",
    borderwidth=1,
    borderpad=4,
    bgcolor="black",
    opacity=0.8,
    font=dict(size=12)
)

# Add more margin space for the explainer text
fig.update_layout(margin=dict(l=50, r=50, t=100, b=120))

st.write("# Klassen in Deutschland - Eine Datenanalyse")

st.write("*Kein support für Mobil Ansicht -> Nutz einen Laptop/Desktop*")

st.write("> *„Auf einmal hören wir wieder etwas über Klassen, aber jahrelang hat man uns erzählt, dass es Klassen nicht mehr wirklich gibt. Nein, wir gehören jetzt alle zur 'Mittelklasse.' "
"Niemand sagt das heute mehr. Das ist wirklich interessant. Zum Teil liegt das daran, dass sie die weiße Arbeiterklasse zum Sündenbock machen wollen! (Mark Fisher)”*")



st.markdown(
    """
    Seit Jahren beschäftigt mich die Frage: **Wer gehört heutzutage zur Arbeiter*innenklasse in Deutschland?**  
    Was mich daran nervt, hat der Soziologe **D. W. Livingstone** treffend formuliert:  
    *"Without solid data, discussions about class and class consciousness are often just guesswork."*  

    Das ist mein bescheidener Versuch, das Rätselraten etwas zu reduzieren und der politischen Linken eine grobe Karte an die Hand zu geben.  
    Ein Großteil der Kategorien und Überlegungen basiert auf den Arbeiten von [D.W Livingstone](https://discover.research.utoronto.ca/27054-dw-livingstone).  

    Die Daten für die Operationalisierung stammen aus dem [**Zensus 2022**](https://ergebnisse.zensus2022.de/datenbank/online/) des Statistischen Bundesamtes.  
    Dabei nutze ich die Variablen **"[Stellung im Beruf](https://ergebnisse.zensus2022.de/datenbank/online/variable/ERWBV1/details/tables)"** und  
    **"[ISCO-08 Codes Level 4](https://ilostat.ilo.org/methods/concepts-and-definitions/classification-occupation/#elementor-toc__heading-anchor-4)"**.  

    Diese Grundlage erlaubt zwar keine direkten Aussagen über Klassenbewusstsein, bietet aber die Möglichkeit,  
    eine aktuelle Skizze der deutschen Klassengesellschaft zu entwerfen.
    """
)

#GRAPH:
st.plotly_chart(fig,use_container_width=True)

with st.expander("Mehr über das Klassenmodel nach D.W Livingstone"):
    base_path = Path(__file__).parent
    image_path = base_path / "assets/images/class_canada_2016.png"
    st.image(str(image_path), caption="Zahlen für Kanada - Screen shoot einer Folie von Livingstone")

    st.markdown(""" 

    #### 🏢 **Owners**  
    - **Corporate Capitalists**  
    - **Large Employers**  
    - **Small Employers / Self-Employed**  

    ---  

    #### 👔 **Managerial Employees**  
    - **Upper Managers**  
    - **Middle Managers**  
    - **Supervisors**  

    ---  

    #### 🛠 **Non-Managerial Workers**  
    - **Professional Employees**  
    - **Service Workers**  
    - **Industrial Workers**  
    """)

#st.plotly_chart(fig,use_container_width=True)


def create_sankey_diagram(df, source_col, target_col, value_col=None, title="Sankey Diagram"):
    """
    Create a Sankey diagram from a dataframe with source and target columns.
    The number of categories is determined dynamically from the data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The input dataframe containing source and target data
    source_col : str
        The name of the source column
    target_col : str
        The name of the target column
    value_col : str, optional
        The name of the value column. If None, all flows will have equal value of 1
    title : str, optional
        The title for the Sankey diagram
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The Sankey diagram figure that can be displayed with fig.show()
    """
    color_high_contrast= ['#004488FF', '#DDAA33FF', '#BB5566FF']

    # Ensure the columns exist in the dataframe
    if source_col not in df.columns:
        raise ValueError(f"Source column '{source_col}' not found in dataframe")
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataframe")
    if value_col and value_col not in df.columns:
        raise ValueError(f"Value column '{value_col}' not found in dataframe")
    
    # Extract unique node labels from both source and target columns
    all_nodes = pd.unique(df[[source_col, target_col]].values.ravel('K'))
    all_nodes = [node for node in all_nodes if node is not None and not pd.isna(node)]
    
    # Create a mapping from node names to indices
    node_indices = {node: i for i, node in enumerate(all_nodes)}
    
    # Convert source and target names to their respective indices
    sources = [node_indices[node] for node in df[source_col]]
    targets = [node_indices[node] for node in df[target_col]]
    
    # Get values for the links
    if value_col:
        values = df[value_col].tolist()
    else:
        values = [1] * len(sources)  # Default to 1 if no value column provided
    
    # Calculate appropriate height based on number of nodes
    # More nodes need more vertical space
    base_height = 600
    height_per_node = 20
    num_nodes = len(all_nodes)
    height = max(base_height, min(3000, base_height + (num_nodes * height_per_node)))
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color='blue'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(100, 100, 200, 0.2)"
        ),
        arrangement="snap"  # This helps with layout
    )])
    
    # Update layout - dynamically adjust size based on node count
    fig.update_layout(
        title_text=title,
        font_size=14,  # Smaller font size
        width=600,
        height=height,  # Dynamic height based on node count
        margin=dict(l=25, r=25, t=50, b=25)
    )
    
    # Add custom hover text
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        node=dict(
            hovertemplate='%{label}<extra></extra>'
        ),
        link=dict(
            hovertemplate='%{source.label} → %{target.label}<br>Value: %{value}<extra></extra>'
        )
    )
    
    return fig


st.markdown(
    """
    ## Betrachte die einzelnen Fraktionen genauer:
    """
)
selected_class_fraction = st.selectbox("Wähle ein Klassen-Fraktion aus", fraktion_order,index=7)

class_data = livingstone_data.query(f'modifiziert_livingstone == "{selected_class_fraction}"')
class_data['meta_category']= selected_class_fraction


sankey_fig =create_sankey_diagram(class_data,'Bezeichnung','meta_category','Anzahl',selected_class_fraction)

st.plotly_chart(sankey_fig,use_container_width=True)