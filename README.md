# Primate Observations Explorer

An interactive web application for exploring and visualizing primate observations across different locations. The application allows users to filter and view research-grade observations of various primate species on an interactive map.

![Golden Monkey Logo](20250530_1246_Golden%20Monkey%20Logo_simple_compose_01jwfr4j0hfe3a5ffebeey2s3h.png)

## Features

- 🗺️ Interactive map visualization with clustering support
- 🐒 Filter observations by primate species
- 📍 Detailed observation information including location and date
- 🖼️ Photo display for observations where available
- 🌍 Option to switch between standard map and Google Maps
- 📊 Real-time observation count display
- 🎨 Color-coded species markers with dynamic legend

## Getting Started

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/monkey_finder_app.git
cd monkey_finder_app
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

### Running the Application

To start the application, run:
```bash
streamlit run app.py
```

The application will open in your default web browser.

## Data Files

The application requires two CSV files:

- `species_list.csv`: Contains information about primate species, including scientific and common names
- `species_observations.csv`: Contains the observation data, including coordinates, dates, and species information

## Usage

1. Use the sidebar to select one or more primate species to display
2. Toggle between standard map view and Google Maps view using the checkbox
3. Click on markers to view detailed information about each observation
4. Use the marker clusters to navigate areas with many observations
5. Refer to the color-coded legend in the sidebar for species identification

## Dependencies

- Streamlit - Web application framework
- Pandas - Data manipulation and analysis
- Folium - Map visualization
- Streamlit-Folium - Streamlit component for Folium maps
- NumPy - Numerical computing tools

## License

[Add your chosen license here]

## Acknowledgments

- Thanks to the contributors who provided primate observation data
- Special thanks to the Streamlit and Folium communities for their excellent tools
