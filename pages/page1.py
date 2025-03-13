import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio

st.set_page_config(layout="wide")


st.text('Das ist ein erster Entwurf einer Klassen Analyse')
fraktion_daten = pd.read_csv('../streamlit/data/processed_data/fraktion_daten.csv')


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

fraktion_order = [
   "Top Management", "Mittleres Management", "Anleitender Beschäftigter",
   "Klassisch selbständige Tätigkeit", "Staatsangestellte",
   "Hochspezialisierte Beschäftigte", "Industriearbeiter", "Dienstleistungsarbeiter"
]

# Create horizontal bar chart
fig = px.bar(
    fraktion_daten,
    x="Anzahl",
    y="fraktion",
    color='major_group',
    orientation='h',
    hover_data={
        'Berufsgattung(ISCO-Stufe 4)': True,
        'Anzahl': True,
        'fraktion': False,
        'major_group': False
    },
    title='Klassenanalyse',
    color_discrete_sequence=colors
)

# Style the silces of the bars with black borders and slight transparency
fig.update_traces(
    marker=dict(line=dict(width=0.5, color='black')),
    opacity=0.8
)

# Configure layout (size, legend, margins)
fig.update_layout(
    autosize=True,
    height=750,
    width=1400,
    legend=dict(
        title="Hauptgruppen ISCO-Stufe 1",
        font=dict(size=12)
    ),
    yaxis=dict(
        title=None,
       categoryorder='array',
       categoryarray=fraktion_order,
    ),
    margin=dict(l=200), #preventing yaxis label cut off
    xaxis=dict(title="Anzahl der Erwerbstätigen in Millionen")  # changes x-axis label
)

# Button to toggle the legend visibility
toggle_button = st.button("Click here to hide legend")

# Update the layout based on button click
if toggle_button:
    # If the button is clicked, hide the legend
    fig.update_layout(showlegend=False)
else:
    # Otherwise, show the legend
    fig.update_layout(showlegend=True)
#fig.show()

st.plotly_chart(fig,use_container_width=True)

#edited_df = st.data_editor(fraktion_daten[['ISCO-Code','Berufsgattung(ISCO-Stufe 4)','fraktion']],hide_index=True)


st.text('Noch ein Plot')

isco_verdienst = pd.read_csv('../streamlit/data/processed_data/isco_verdienst.csv')

def pipline_data_bubble_chart(df):
    df = df[['fraktion','Anzahl','Berufsgattung(ISCO-Stufe 4)','median_brutto_group_mean']]

    df.columns =['category', 'size_markers','subcategory','value_y_axis']
    df=df.replace('/','0')
    df['size_markers'] = df['size_markers'].astype(float)
    df.dropna(inplace=True)
    df['scale_markers'] = df['size_markers'] /20000
    return df


def generate_bubble_swarm_chart(df):
    # Validate input DataFrame
    required_columns = ['category', 'size_markers', 'value_y_axis']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    # Ensure categories are strings
    df['category'] = df['category'].astype(str)

    # Get unique categories and assign colors
    categories = df['category'].unique()
    colors = [
        'rgba(31, 119, 180, 0.7)',  # Blue
        'rgba(255, 127, 14, 0.7)',  # Orange
        'rgba(44, 160, 44, 0.7)',   # Green
    ]

    # Extend colors if needed
    if len(categories) > len(colors):
        additional_colors = [
            f'rgba({np.random.randint(0,256)}, {np.random.randint(0,256)}, {np.random.randint(0,256)}, 0.7)'
            for _ in range(len(categories) - len(colors))
        ]
        colors.extend(additional_colors)

    # Create category to position mapping
    cat_to_pos = {cat: i for i, cat in enumerate(categories)}
    
    # Create traces
    traces = []
    for i, category in enumerate(categories):
        category_df = df[df['category'] == category].copy()
        
        # Create x positions with jitter or spread out
        base_x = cat_to_pos[category]
        x_jittered = np.random.normal(loc=base_x, scale=0.15, size=len(category_df))
        
        trace = go.Scatter(
            x=x_jittered,
            y=category_df['value_y_axis'],
            mode='markers',
            name=f'{category} (n={len(category_df)})',
            marker=dict(
                size=category_df['scale_markers'],
                color=colors[i],
                line=dict(width=1, color='rgba(0,0,0,0.5)'),
                opacity=0.7
            ),
            text=[f'<br>Subcategory: {subcategory}<br>Gehalt: {y:.2f}<br>Anzahl: {size:.2f}'
                  for y, size, subcategory in zip(category_df['value_y_axis'],
                                                category_df['size_markers'],
                                                category_df['subcategory'])],
            hoverinfo='text'
        )
        traces.append(trace)

    
    # Create layout
    layout = go.Layout(
            title=dict(
                text='Klassenanalyse mit ISCO-Berufsgattung auf Basis von Zensusdaten',
                font=dict(
                    size=24,  # Set the title font size
                    color='white'  # Optional: Set the title font color
                ),
                x=0  # Center the title horizontally (optional)
            ),
        height=850,
        width=700,
        xaxis=dict(
            title='Arbeiterklassenfraktionen',
            ticktext=list(categories),
            tickvals=list(range(len(categories))),
            tickmode='array',
            zeroline=False,  # Hide the zero line to avoid conflicts
            showline=True,  # Force the x-axis line to appear
            linecolor='black',  # Make the x-axis line visible
            linewidth=2,  # Set the line width
        ),
        yaxis=dict(
            title='Monatsbrutto Gehalt',
            rangemode='tozero',
            zeroline=False,  # Hide the zero line
            showline=True,  # Force the y-axis line to appear
            linecolor='black',  # Make the y-axis line visible
            linewidth=2,  # Set the line width
            side='left',  # Ensure the y-axis is positioned on the left
            overlaying='free',  # Ensure it is not dependent on the categories
            position=0  # Explicitly place y-axis at x=0
        ),
        margin=dict(l=100),  # Add some left margin to ensure axis labels are visible
        hovermode='closest',
        showlegend=False
    )

    # Create and show figure
    fig = go.Figure(data=traces, layout=layout)
    return fig

#TODO do I want only plot working class
filtered_data = isco_verdienst[
    isco_verdienst['fraktion'].isin(['Hochspezialisierte Beschäftigte', 'Industriearbeiter', 'Dienstleistungsarbeiter'])
]

#prepare labeling an structur for graph
income_data_test=pipline_data_bubble_chart(filtered_data)

#Dropping Fluglotsen
income_data_test.drop(index=[133, 134], inplace=True)

st.plotly_chart(generate_bubble_swarm_chart(income_data_test))