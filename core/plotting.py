import numpy as np
import pandas as pd
import skfuzzy as fuzz
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap

# Load your existing dataset
file_path = "D:\SIH FAIR\AEGISDataset.csv"

def load_dataset(file_path):
    df = pd.read_csv(file_path)
    # Ensure column names are correct
    if 'latitude' in df.columns:
        df.rename(columns={'latitude': 'lat'}, inplace=True)
    if 'longitude' in df.columns:
        df.rename(columns={'longitude': 'lon'}, inplace=True)
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

# Fuzzy risk calculation
def calculate_risk(row, fuzzy_functions):
    # Default values if columns are missing
    proximity = row.get('proximity', 50)
    elevation = row.get('elevation', 50)
    
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
    
    response_status = row.get('responded', 0)
    geographic_risk = 1 - abs(row['lat'] - 12.8797) / 2 - abs(row['lon'] - 121.7740) / 2
    
    risk_factors = [
        proximity_level_near,
        elevation_level_low,
        1 if response_status else 0,
        geographic_risk
    ]
    
    overall_risk = np.mean(risk_factors) * 10
    return min(max(overall_risk, 0), 10)

# Create interactive map
def create_flood_risk_map(prioritized_rescue):
    def get_risk_color(risk):
        if risk <= 3:
            return 'green'
        elif risk <= 6:
            return 'orange'
        else:
            return 'red'

    philippines_map = folium.Map(location=[12.8797, 121.7740], zoom_start=6)

    for _, row in prioritized_rescue.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=get_risk_color(row['flood_risk']),
            fill=True,
            fill_color=get_risk_color(row['flood_risk']),
            fill_opacity=0.7,
            popup=f"ID: {row.get('id', 'N/A')}<br>Risk: {row['flood_risk']:.2f}"
        ).add_to(philippines_map)

    heat_data = [[row['lat'], row['lon'], row['flood_risk']] for _, row in prioritized_rescue.iterrows()]
    HeatMap(heat_data, min_opacity=0.4, radius=10).add_to(philippines_map)

    philippines_map.save("philippines_flood_risk_map.html")

# Main analysis function
def flood_risk_analysis(file_path):
    # Load dataset
    flood_data = load_dataset(file_path)
    
    # Create fuzzy membership functions
    fuzzy_functions = create_fuzzy_membership_functions()
    
    # Calculate risk for each location
    flood_data['flood_risk'] = flood_data.apply(
        lambda row: calculate_risk(row, fuzzy_functions), 
        axis=1
    )
    
    # Sort by risk and geographic clustering
    prioritized_rescue = flood_data.sort_values(
        ['flood_risk', 'lat', 'lon'], 
        ascending=[False, True, True]
    )
    
    # Analysis outputs
    print("Flood Risk Distribution:")
    risk_bins = pd.cut(
        prioritized_rescue['flood_risk'], 
        bins=[0, 3, 6, 10], 
        labels=['Low', 'Moderate', 'High']
    )
    print(risk_bins.value_counts(normalize=True) * 100)

    print("\nTop 10 Highest Risk Locations:")
    top_10_columns = ['id', 'lat', 'lon', 'flood_risk'] if 'id' in prioritized_rescue.columns else ['lat', 'lon', 'flood_risk']
    top_10 = prioritized_rescue.head(10)[top_10_columns]
    print(top_10)

    # Visualization of risk distribution
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        prioritized_rescue['lon'], 
        prioritized_rescue['lat'], 
        c=prioritized_rescue['flood_risk'], 
        cmap='YlOrRd', 
        alpha=0.5
    )
    plt.colorbar(scatter, label='Flood Risk')
    plt.title('Flood Risk Distribution')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()
    plt.show()

    # Create interactive map
    create_flood_risk_map(prioritized_rescue)

    # Save top high-risk locations to CSV
    top_100_columns = ['id', 'lat', 'lon', 'flood_risk'] if 'id' in prioritized_rescue.columns else ['lat', 'lon', 'flood_risk']
    top_100_high_risk = prioritized_rescue.head(100)[top_100_columns]
    top_100_high_risk.to_csv('top_100_high_risk_locations.csv', index=False)

# Run the analysis (replace with your actual file path)
if __name__ == "__main__":
    flood_risk_analysis(r"D:\SIH FAIR\AEGISDataset.csv")

def create_flood_risk_map(prioritized_rescue):
    def get_risk_color(risk):
        if risk <= 3:
            return 'green'
        elif risk <= 6:
            return 'orange'
        else:
            return 'red'

    # Center map on Philippines
    philippines_map = folium.Map(location=[12.8797, 121.7740], zoom_start=6)

    # Add markers for each location
    for _, row in prioritized_rescue.iterrows():
        # Create popup with detailed information
        popup_text = f"""
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
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(philippines_map)

    # Add heatmap layer
    heat_data = [[row['lat'], row['lon'], row['flood_risk']] for _, row in prioritized_rescue.iterrows()]
    HeatMap(heat_data, min_opacity=0.4, radius=10).add_to(philippines_map)

    # Save map
    philippines_map.save("philippines_flood_risk_map.html")