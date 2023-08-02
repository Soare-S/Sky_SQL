import folium
import os
import matplotlib.colors as mcolors
import matplotlib.cm as cm


def plotting_delayed_map(get_delays, get_coordinates):
    # Create a map centered on the United States
    map_center = [37.0902, -95.7129]  # Coordinates of the United States
    map_zoom = 4  # Zoom level of the map
    flight_map = folium.Map(location=map_center, zoom_start=map_zoom)
    # Print a message to check if the map is created
    print("Map created successfully")

    # Get a colormap for the colors
    cmap = cm.get_cmap('Accent')  # You can use any other colormap of your choice

    # Plot the routes and connecting lines on the map
    for row in get_delays:
        origin_airport = row['ORIGIN_AIRPORT']
        dest_airport = row['DESTINATION_AIRPORT']
        percentage = row['percentage']

        # Ensure that the percentage value is within the expected range [0, 1]
        updated_percentage = percentage / 100  # Clip the value to [0, 1]

        # Convert the percentage value to an RGB sequence using the colormap
        color_rgb = cmap(updated_percentage)[:3]  # Extract RGB values from the colormap
        color_hex = mcolors.rgb2hex(color_rgb)

        origin_lat, origin_lon = get_coordinates[origin_airport]["lat"], get_coordinates[origin_airport]["long"]
        dest_lat, dest_lon = get_coordinates[dest_airport]["lat"], get_coordinates[dest_airport]["long"]
        origin_coords = (origin_lat, origin_lon)
        destination_coords = (dest_lat, dest_lon)

        line = folium.PolyLine(
            locations=[origin_coords, destination_coords],
            color=color_hex,
            weight=2,
            opacity=0.7,
            popup=f"{origin_airport} to {dest_airport}<br>Percentage: {percentage:.2f}%"
        )
        # Adding the PolyLine
        flight_map.add_child(line)

    # Save the map as an HTML file
    file_path = os.path.join("templates", "flight_map.html")
    flight_map.save(file_path)
    return file_path
