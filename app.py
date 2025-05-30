import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np
from folium.plugins import MarkerCluster

# Set page config
st.set_page_config(page_title="Species Observations Map", layout="wide")

# Title
st.title("Species Observations Map")

# Read the data
@st.cache_data
def load_data():
    # Read observations and species list
    df = pd.read_csv('species_observations.csv')
    species_list = pd.read_csv('species_list.csv')
    
    # Create full scientific name in species list to match with observations
    species_list['full_name'] = species_list['genus'] + ' ' + species_list['species']
    
    # Merge common names into observations
    df = df.merge(species_list[['full_name', 'common']], 
                 left_on='search_species', 
                 right_on='full_name', 
                 how='left')
    
    # Filter for research grade records only
    df = df[df['quality_grade'] == 'research']
    return df

# Load the data
df = load_data()

# Get unique species for color mapping
unique_species = df['search_species'].unique()
colors = [f'#{np.random.randint(0, 16777215):06x}' for _ in range(len(unique_species))]
color_map = dict(zip(unique_species, colors))

# Create display names for species (common name + scientific name)
species_display = {}
for species in unique_species:
    common_name = df[df['search_species'] == species]['common'].iloc[0]
    species_display[species] = f"{common_name} ({species})"

# Create species selection
selected_species = st.multiselect(
    'Select species to display',
    options=list(unique_species),
    format_func=lambda x: species_display[x],
    default=[]
)

# Filter data based on selection
if selected_species:
    filtered_df = df[df['search_species'].isin(selected_species)]
else:
    filtered_df = df

# Create map controls
col1, col2 = st.columns([2, 1])
with col1:
    st.write(f"Showing {len(filtered_df)} research grade observations")
with col2:
    use_google_maps = st.toggle('Use Google Maps')

# Create map with appropriate tiles
if use_google_maps:
    m = folium.Map(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                   attr='Google Maps',
                   control_scale=True)
else:
    m = folium.Map(control_scale=True)

# Create a marker cluster for better performance
marker_cluster = MarkerCluster().add_to(m)

# Add points to the map
for idx, row in filtered_df.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):        # Create popup content
        popup_content = f"""
        <b>Common Name:</b> {row['common']}<br>
        <b>Scientific Name:</b> {row['search_species']}<br>
        <b>Date:</b> {row['observed_on']}<br>
        <b>Location:</b> {row['place']}<br>
        """
        if pd.notna(row['photo_url']):
            popup_content += f"<img src='{row['photo_url']}' width='200px'>"
        
        # Add marker
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row['search_species'],
            color=color_map[row['search_species']],
            fill=True,
            fill_opacity=0.7
        ).add_to(marker_cluster)

# Adjust map bounds to show all points
if not filtered_df.empty:
    sw = filtered_df[['latitude', 'longitude']].min().values.tolist()
    ne = filtered_df[['latitude', 'longitude']].max().values.tolist()
    m.fit_bounds([sw, ne])

# Display map
st.write("### Observation Map")
folium_static(m, width=1200, height=800)

# Display color legend
st.write("### Species Color Legend")
legend_cols = st.columns(4)
for i, (species, color) in enumerate(color_map.items()):
    if species in selected_species:
        legend_cols[i % 4].markdown(            f"<div style='display: flex; align-items: center; margin-bottom: 5px;'>"
            f"<div style='width: 20px; height: 20px; background-color: {color}; "
            f"border-radius: 50%; margin-right: 8px;'></div>"
            f"<div>{filtered_df[filtered_df['search_species'] == species]['common'].iloc[0]}<br>"
            f"<small><i>{species}</i></small></div></div>",
            unsafe_allow_html=True
        )
