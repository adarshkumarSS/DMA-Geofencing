import numpy as np
import pandas as pd
import skfuzzy as fuzz
import folium
from folium.plugins import HeatMap

# Load dataset
file_path = "D:\SIH FAIR\AEGISDataset.csv"

def load_dataset(file_path):
    df = pd.read_csv(file_path)
    # Rename columns if necessary
    column_mapping = {
        'latitude': 'lat', 
        'longitude': 'lon',
        'Latitude': 'lat', 
        'Longitude': 'lon'
    }
    df.rename(columns=column_mapping, inplace=True)
    return df

# Fuzzy logic membership functions
def create_fuzzy_membership_functions():
    proximity_range = np.arange(0, 101, 1)
    elevation_range = np.arange(0, 101, 1)
    flood_risk_range = np.arange(0, 11, 1)

    proximity_near = fuzz.trapmf(proximity_range, [0, 0, 10, 30])
    elevation_low = fuzz.trapmf(elevation_range, [0, 0, 20, 40])

    return {
        'proximity_range': proximity_range,
        'elevation_range': elevation_range,
        'flood_risk_range': flood_risk_range,
        'proximity_near': proximity_near,
        'elevation_low': elevation_low
    }

# Risk calculation function
def calculate_flood_risk(row, fuzzy_functions):
    # Handle missing or default values
    proximity = row.get('proximity', 50)
    elevation = row.get('elevation', 50)
    
    # Fuzzy membership calculations
    proximity_level_near = fuzz.interp_membership(
        fuzzy_functions['proximity_range'], 
        fuzzy_functions['proximity_near'], 
        proximity
    )
    elevation_level_low = fuzz.interp_membership(
        fuzzy_functions['elevation_range'], 
        fuzzy_functions['elevation_low'], 
        elevation
    )
    
    # Calculate geographic risk based on location
    geographic_risk = 1 - abs(row['lat'] - 12.8797) / 2 - abs(row['lon'] - 121.7740) / 2
    
    # Combine risk factors
    risk_factors = [
        proximity_level_near,
        elevation_level_low,
        geographic_risk
    ]
    
    # Calculate and normalize overall risk
    overall_risk = np.mean(risk_factors) * 10
    return min(max(overall_risk, 0), 10)

# Create Folium map with risk visualization
def create_risk_map(flood_data):
    # Determine map center
    center_lat = flood_data['lat'].mean()
    center_lon = flood_data['lon'].mean()
    
    # Create base map
    risk_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)
    
    # Color coding function for risk levels
    def get_risk_color(risk):
        if risk <= 3:
            return 'green'
        elif risk <= 6:
            return 'orange'
        else:
            return 'red'
    
    # Add markers for each location
    for idx, row in flood_data.iterrows():
        # Create detailed popup
        popup_content = f"""
        Latitude: {row['lat']:.4f}
        Longitude: {row['lon']:.4f}
        Flood Risk: {row['flood_risk']:.2f}
        """
        
        # Add circle marker
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=get_risk_color(row['flood_risk']),
            fill=True,
            fill_color=get_risk_color(row['flood_risk']),
            fill_opacity=0.7,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(risk_map)
    
    # Add heatmap layer
    heat_data = [[row['lat'], row['lon'], row['flood_risk']] for idx, row in flood_data.iterrows()]
    HeatMap(heat_data, name='Flood Risk Heatmap').add_to(risk_map)
    
    # Save map
    risk_map.save('flood_risk_map.html')
    print("Flood risk map saved as 'flood_risk_map.html'")

# Main analysis function
def flood_risk_analysis(file_path):
    # Load dataset
    flood_data = load_dataset(file_path)
    
    # Create fuzzy membership functions
    fuzzy_functions = create_fuzzy_membership_functions()
    
    # Calculate flood risk for each location
    flood_data['flood_risk'] = flood_data.apply(
        lambda row: calculate_flood_risk(row, fuzzy_functions), 
        axis=1
    )
    
    # Sort by flood risk in descending order
    prioritized_locations = flood_data.sort_values('flood_risk', ascending=False)
    
    # Create and save risk map
    create_risk_map(prioritized_locations)
    
    # Print top 10 high-risk locations
    print("\nTop 10 Highest Risk Locations:")
    print(prioritized_locations[['lat', 'lon', 'flood_risk']].head(10))
    
    return prioritized_locations

# Execute analysis
if __name__ == "__main__":
    file_path = r"D:\SIH FAIR\AEGISDataset.csv"
    results = flood_risk_analysis(file_path)