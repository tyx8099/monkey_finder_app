import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np
from folium.plugins import MarkerCluster
import concurrent.futures
from functools import partial

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'species_display' not in st.session_state:
    st.session_state.species_display = None
if 'color_map' not in st.session_state:
    st.session_state.color_map = None
if 'unique_species' not in st.session_state:
    st.session_state.unique_species = None

# Set page config
st.set_page_config(
    page_title="Primate Observations Explorer",
    page_icon="20250530_1246_Golden Monkey Logo_simple_compose_01jwfr4j0hfe3a5ffebeey2s3h.png",
    layout="wide"
)

# Cache data loading
@st.cache_data
def load_data():
    # Load and prepare species data
    species_df = pd.read_csv('species_list.csv')
    species_df['search_species'] = species_df['genus'] + ' ' + species_df['species']
    
    # Create display names
    species_display = {}
    for _, row in species_df.iterrows():
        if pd.notna(row['common']) and pd.notna(row['search_species']):
            species_display[row['search_species']] = f"{row['common']} ({row['search_species']})"
      # Load observations data
    observations_df = pd.read_csv('species_observations.csv')
    
    # Make sure observations have all required fields
    if 'common' not in observations_df.columns:
        # Merge observations with species information to get common names
        observations_df = observations_df.merge(
            species_df[['search_species', 'common', 'genus', 'species']],
            on='search_species',
            how='left'
        )
      # Ensure all required fields are present
    required_fields = ['latitude', 'longitude', 'search_species', 'common', 'place', 'observed_on']
    missing_fields = [field for field in required_fields if field not in observations_df.columns]
    
    if 'common' in missing_fields:
        # Merge with species data to get common names
        observations_df = observations_df.merge(
            species_df[['search_species', 'common']],
            on='search_species',
            how='left'
        )
    
    # Final cleanup of any remaining NaN values
    observations_df = observations_df.dropna(subset=required_fields)
      # Get only species that have observations
    unique_species = observations_df['search_species'].unique()
    species_counts = observations_df['search_species'].value_counts()
    available_species = [species for species in unique_species if species_counts[species] > 0]
    
    # Create color map using only species with observations
    colors = [f'#{hash(species) % 0xFFFFFF:06x}' for species in available_species]
    color_map = dict(zip(available_species, colors))
    
    # Create species info dictionary with counts
    species_info = {species: f"{species_display.get(species, species)} ({species_counts[species]} observations)" 
                   for species in available_species}
    
    return observations_df, species_info, color_map, available_species

# Load data into session state if not already loaded
if st.session_state.data is None:
    observations_df, species_display, color_map, unique_species = load_data()
    st.session_state.data = observations_df
    st.session_state.species_display = species_display
    st.session_state.color_map = color_map
    st.session_state.unique_species = unique_species

# Sidebar setup with logo
with st.sidebar:
    # Display logo at the top of sidebar
    st.title("Filters")
    
    # Species selection
    selected_species = st.multiselect(
        'Select species to display',
        options=list(st.session_state.unique_species),
        format_func=lambda x: st.session_state.species_display[x],
        default=[]
    )
    
    # Map type selection
    use_google_maps = st.checkbox('Use Google Maps', value=False)

# Filter data based on selection (now operates on in-memory data)
def filter_observations(selected_species):
    if not selected_species:
        return pd.DataFrame(columns=st.session_state.data.columns)  # Return empty DataFrame with same structure
    return st.session_state.data[st.session_state.data['search_species'].isin(selected_species)]

filtered_df = filter_observations(selected_species)

# Show observation count with valid coordinates
st.write(f"Showing {len(filtered_df)} research grade observations")

# Create map function (removed caching for smoother updates)
def create_map(filtered_df, color_map, use_google_maps):
    # Create base map with appropriate tiles
    if use_google_maps:
        m = folium.Map(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google Maps',
            control_scale=True
        )
    else:
        m = folium.Map(control_scale=True)
    
    # Create a marker cluster for better performance
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add points to the map
    for idx, row in filtered_df.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):            # Create popup content with photo if available
            popup_content = f"""
                <div style='min-width: 200px;'>
                    <b>Species:</b> {row['common']}<br>
                    <b>Scientific name:</b> {row['search_species']}<br>
                    <b>Location:</b> {row['place']}<br>
                    <b>Date:</b> {row['observed_on']}<br>
                </div>
            """
            if pd.notna(row.get('photo_url')):
                # Replace square thumbnail with medium size image
                photo_url = row['photo_url'].replace('square', 'medium')
                popup_content = popup_content.rstrip() + f"<img src='{photo_url}' style='width: 300px; margin-top: 10px; border-radius: 4px;'>"
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{row['common']} ({row['search_species']})",
                color=color_map[row['search_species']],
                fill=True,
                fill_opacity=0.7
            ).add_to(marker_cluster)
    
    # Adjust map bounds to show all points
    if not filtered_df.empty:
        sw = filtered_df[['latitude', 'longitude']].min().values.tolist()
        ne = filtered_df[['latitude', 'longitude']].max().values.tolist()
        m.fit_bounds([sw, ne])
    
    return m

# Remove default padding and expand map width
st.markdown("""
    <style>
        .main > div {
            padding-left: 0;
            padding-right: 0;
        }
    </style>
""", unsafe_allow_html=True)

# Display map in the main area
st.write("### Observation Map")
m = create_map(filtered_df, st.session_state.color_map, use_google_maps)
folium_static(m, height=800, width=1600)  # Increased width for larger display

# Display species legend in the sidebar
with st.sidebar:
    st.write("### Species Legend")
    if not selected_species:
        st.info("Select species from above to see their observations on the map")
    else:
        for species, color in st.session_state.color_map.items():
            if species in selected_species:
                display_name = st.session_state.species_display[species]
                common_name = display_name.split(' (')[0]  # Extract common name from display name
                # Only show the legend item if we have data for this species
                species_data = st.session_state.data[st.session_state.data['search_species'] == species]
                if not species_data.empty:
                    st.markdown(
                        f"<div style='display: flex; align-items: center; margin-bottom: 10px;'>"
                        f"<div style='width: 20px; height: 20px; background-color: {color}; "
                        f"border-radius: 50%; margin-right: 8px; flex-shrink: 0;'></div>"
                        f"<div style='font-size: 0.9em;'>{common_name}<br>"
                        f"<small><i>{species}</i></small></div></div>",
                        unsafe_allow_html=True
                    )
