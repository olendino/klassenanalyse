import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Any
from openpyxl import load_workbook
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from pathlib import Path
from plotly.subplots import make_subplots

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

    merged_data.loc[merged_data['Stellung.im.Beruf'] == 'Selbstständige ohne Beschäftigte', 'modifiziert_livingstone'] = 'Selbstständige'

    # Keep 'Selbstständige mit Beschäftigten' as is 
    # (this line isn't necessary if you don't need to change it, but included for clarity)
    merged_data.loc[merged_data['Stellung.im.Beruf'] == 'Selbstständige mit Beschäftigten', 'modifiziert_livingstone'] = 'Selbstständige mit Beschäftigten'
    
    return merged_data


livingstone_data = set_up_data()




# TODO fix nans (Offiziere)

#TODO
#livingstone_data_clean = livingstone_data.dropna(subset=["modifiziert_livingstone"]) # -> ???

# Custom colors for different categories
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

meta_categories = ["Eigentümer", "Management", "Arbeitende"]
subcategories = {
    "Eigentümer": ["Selbstständige", "Selbstständige mit Beschäftigten"],
    "Management": ["Anleitende Beschäftigte", "Mittleres Management", "Top Management"],
    "Arbeitende": ["Dienstleistungsarbeiter*innen", "Industriearbeiter*innen","Hochspezialisierte Beschäftigte"]
}

# Create two-level y-axis structure from DataFrame
unique_categories = []
y_level1 = []
y_level2 = []
# Maintain order from original structure
# just a transformation of the meta_categories and subcategories into a matrix (two-lists) format
for meta_cat in meta_categories:
    for sub_cat in subcategories[meta_cat]:
        if sub_cat not in unique_categories:
            unique_categories.append(sub_cat)
            y_level1.append(meta_cat)
            y_level2.append(sub_cat)

y_labels = [y_level1, y_level2]

# Calculate total for percentage calculation
total_anzahl = livingstone_data['Anzahl'].sum()

fig = go.Figure()

# Store cumulative values for percentage positioning
cumulative_values = [0] * len(unique_categories)

# Add trace for each group
for group in livingstone_data['major_group'].unique():
    group_data = livingstone_data[livingstone_data['major_group'] == group]
    
    # Ensure data is in the same order as y_labels
    ordered_counts = []
    for i, category in enumerate(unique_categories):
        # MINIMAL FIX: Handle missing data gracefully
        matching_rows = group_data[group_data['modifiziert_livingstone'] == category]
        if len(matching_rows) > 0:
            count = matching_rows['Anzahl'].sum()
        else:
            count = 0  # Default to 0 if category not found
        ordered_counts.append(count)
        cumulative_values[i] += count
    
    fig.add_trace(go.Bar(
        y=y_labels,
        x=ordered_counts,
        name=group,
        orientation='h',
    ))

# Add percentage annotations at the end of each bar
for i, (category, total_value) in enumerate(zip(unique_categories, cumulative_values)):
    if total_value > 0:  # Only add annotation if there's a value
        percentage = (total_value / total_anzahl) * 100
        fig.add_annotation(
            x=total_value + (max(cumulative_values) * 0.01),  # Slight offset from the end of bar
            y=i,
            text=f"{percentage:.1f}%",
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=11, color="white")
        )

fig.update_layout(
    barmode='stack',
    width=1050,  # Reduce width
    height=625,
    yaxis={
        'title': 'Klassen',  # Add a title for the y-axis
        'title_standoff': 25,  # Distance between the axis and its title
        'tickfont': {'size': 12},  # Font size for the tick labels
        'titlefont': {'size': 14, 'color': 'black'}  # Font for the axis title
    },
    xaxis={
        'title':'Anzahl in Millionen'
    },
    margin=dict(l=150, r=100),  # Increased right margin for percentage labels
    legend=dict(
        yanchor="bottom",
        y=0.2,
        xanchor="right",
        x=1.30,
        bgcolor="black",
        bordercolor="rgba(0,0,0,0.2)",
        borderwidth=1,
        title_text='ISCO-08 Hauptgruppen',
        orientation="h",
        font=dict(size=10),  # Reduce legend text size (default is ~12)
        title_font=dict(size=12)
    ),
    plot_bgcolor='black',  # White background
    legend_title_text='ISCO-08 Hauptgruppen',
    showlegend=True  # <-- Switch off legend
)

# Add source information at the bottom
fig.add_annotation(
    text="Quelle: Zensus 2022 | Statistisches Bundesamt",
    showarrow=False,
    xref="paper", yref="paper",
    x=-0.2, y=-0.055,
    xanchor="center", yanchor="top",
    font=dict(size=12, color="gray")
)

# Add reading explanation box
fig.add_annotation(
    text="Der Graph zeigt die Anzahl der verschieden Klassenfraktionen auf Basis der Variablen: \"Stellung im Beruf\" und \"ISCO-08\" der Zensus 2022.",
    showarrow=False,
    xref="paper", yref="paper",
    x=0.4, y=-0.118,
    xanchor="center", yanchor="top",
    bordercolor="lightgrey",
    borderwidth=1,
    borderpad=4,
    bgcolor="black",
    opacity=0.8,
    font=dict(size=12)
)







st.write("# Klassen in Deutschland - Eine Datenanalyse")

st.write("*Kein support für Mobil Ansicht -> Nutz einen Laptop/Desktop*")

#st.write("> *„Auf einmal hören wir wieder etwas über Klassen, aber jahrelang hat man uns erzählt, dass es Klassen nicht mehr wirklich gibt. Nein, wir gehören jetzt alle zur 'Mittelklasse.' "
#"Niemand sagt das heute mehr. Das ist wirklich interessant. Zum Teil liegt das daran, dass sie die weiße Arbeiterklasse zum Sündenbock machen wollen! (Mark Fisher)”*")

#Was mich daran nervt, hat der Soziologe **D. W. Livingstone** treffend formuliert:  *"Without solid data, discussions about class and class consciousness are often just guesswork."* 

st.markdown(
    """
    Seit Jahren beschäftigt mich die Frage: **Wer gehört heutzutage zur Arbeiter*innenklasse in Deutschland?**   

    Das ist mein bescheidener Versuch, das Rätselraten etwas zu reduzieren und der politischen Linken eine grobe Karte an die Hand zu geben.  
    Ein Großteil der Kategorien und Überlegungen basiert auf den Arbeiten von [D.W Livingstone](https://discover.research.utoronto.ca/27054-dw-livingstone). 
    Sein Klassenmodell basiert auf einem klassisch marxistischen Ansatz und empirischen Daten, die er im Rahmen seiner Bildungsforschung erhoben hat. 
    Die folgende Grafik gibt einen Überblick über die drei Klassen und zehn Klassenfraktionen.
    """)
base_path = Path(__file__).parent
image_path = base_path / "assets/images/class_canada_2016.png"
st.image(str(image_path), caption="Zahlen für Kanada - Screen shoot einer Folie von Livingstone")

st.markdown(
    """
    Die folgende Datenanalyse ist im wesentlichen der Versuch diese für Deutschland anzupassen und emprisch aufzubereiten.
    Die Daten für die Operationalisierung stammen aus dem [**Zensus 2022**](https://ergebnisse.zensus2022.de/datenbank/online/) des Statistischen Bundesamtes.  
    Dabei nutze ich die Variablen **"[Stellung im Beruf](https://ergebnisse.zensus2022.de/datenbank/online/variable/ERWBV1/details/tables)"** und  
    **"[ISCO-08 Codes Level 4](https://ilostat.ilo.org/methods/concepts-and-definitions/classification-occupation/#elementor-toc__heading-anchor-4)"**.  

    Diese Grundlage erlaubt zwar keine direkten Aussagen über Klassenbewusstsein, bietet aber die Möglichkeit,  
    eine aktuelle Skizze der deutschen Klassengesellschaft zu entwerfen.
    """
)

#GRAPH:
st.plotly_chart(fig,use_container_width=True)


#st.plotly_chart(fig,use_container_width=True)



def create_treemap(df, source_col, target_col, value_col=None, title="Treemap Diagram"):
    """
    Create a treemap where sources are nested under their respective targets, sized by flow.
    """

    fig = px.treemap(
        df,
        path=[target_col, source_col],
        values=value_col,
        color=target_col,
        title=title
    )
    fig.update_traces(
        textinfo="label+value",  # Show both label and value
        textfont=dict(size=16),  # Slightly bigger text
        textposition='middle center',
        hovertemplate='<b>%{label}</b><br>Abs. Anzahl: %{value:..0f}<extra></extra>'  # Customized hover text
    )

    fig.update_layout(
        height=800,
        margin=dict(t=50, l=25, r=25, b=25),
        hoverlabel=dict(
            bgcolor="black",
            font_size=20
        )
    )

    return fig

st.markdown(
    """
    ## Betrachte die einzelnen Fraktionen genauer:
    Hier kannst du eine der oberen Fraktionen (zweite Ebene der Y-Achse) auswählen, um die jeweilige Klassenfraktion auf ihrer untersten Ebene der Berufsgruppe (ISCO-08 Level 4) dargestellt zu bekommen.
    Das ermöglicht besser zu verstehn woraus die Klassenfraktionen gebildet sind und welche Beruf(sgruppen) zu ihnen zählen.
    """
)



selected_class_fraction_treemap = st.selectbox(
    "Wähle ein Klassen-Fraktion aus",
      livingstone_data['modifiziert_livingstone'].unique(),index=7,
      key="treemap_selector"
)

class_fraction_data = livingstone_data.query(f'modifiziert_livingstone == "{selected_class_fraction_treemap}"')
class_fraction_data.loc[:,'meta_category']= selected_class_fraction_treemap


treemap_fig =create_treemap(class_fraction_data,'Bezeichnung','meta_category','Anzahl',selected_class_fraction_treemap)

st.plotly_chart(treemap_fig,use_container_width=True)