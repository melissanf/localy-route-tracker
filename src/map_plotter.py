import folium
import os

def initialize_map(center_coordinates, zoom_start=14):
    """Initialize a Folium map centered at given coordinates"""
    lat, lon = center_coordinates
    return folium.Map(location=[lat, lon], zoom_start=zoom_start)


def add_colored_marker(map_object, coordinate, marker_color, tooltip_text="", popup_text=""):
    """
    Add a colored marker to the map.
    marker_color: 'green', 'red', 'blue', etc.
    """
    lat, lon = coordinate

    marker = folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(color=marker_color, icon='info-sign'),
        tooltip=tooltip_text
    )
    
    if popup_text:
        marker = folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color=marker_color, icon='info-sign'),
            tooltip=tooltip_text,
            popup=folium.Popup(popup_text, max_width=300)
        )
    
    marker.add_to(map_object)


def draw_route(map_object, coordinates_list):
    """Draw a route line connecting the coordinates"""
    folium.PolyLine(
        coordinates_list,
        color='#173DED',
        weight=4,
        opacity=0.8
    ).add_to(map_object)


def adjust_map_view(map_object, coordinates_list):
    """Adjust the map view to fit all coordinates"""
    map_object.fit_bounds(coordinates_list)


def save_map(map_object, output_path):
    """Save the map to an HTML file"""
    directory = os.path.dirname(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    map_object.save(output_path)


def generate_itinerary_map(photo_points, output_path="data/output/route_map.html"):
    """
    Generate an itinerary map from photo points.
    Photo points should have: filename, latitude, longitude, timestamp (optional)
    """
    
    if len(photo_points) == 0:
        print("Aucune donnée GPS trouvée. Impossible de générer la carte.")
        return None

    # 1. Sort by timestamp if available
    photo_points_sorted = sorted(
        photo_points, 
        key=lambda x: x.get("timestamp", "") or ""
    )

    # 2. Extract coordinates
    coordinates = [
        [p["latitude"], p["longitude"]]
        for p in photo_points_sorted
    ]

    # 3. Initialize map centered on first point
    first_point = coordinates[0]
    route_map = initialize_map(first_point)

    # 4. Add numbered markers with colors
    for i, point in enumerate(photo_points_sorted):
        coord = (point["latitude"], point["longitude"])
        filename = point.get("filename", "")
        timestamp = point.get("timestamp", "")
        
        # Format timestamp for display
        time_display = ""
        if timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                time_display = dt.strftime("%d/%m/%Y %H:%M")
            except:
                time_display = timestamp
        
        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <b>Point {i+1}</b><br>
            <small>{filename}</small><br>
            {f'<small>📅 {time_display}</small>' if time_display else ''}
        </div>
        """
        
        # First point = green (start)
        if i == 0:
            add_colored_marker(
                route_map, coord, "green", 
                tooltip_text=f"Départ: {filename}",
                popup_text=popup_content
            )

        # Last point = red (end)
        elif i == len(photo_points_sorted) - 1:
            add_colored_marker(
                route_map, coord, "red", 
                tooltip_text=f"Arrivée: {filename}",
                popup_text=popup_content
            )

        # Middle points = blue
        else:
            add_colored_marker(
                route_map, coord, "blue", 
                tooltip_text=f"Point {i+1}: {filename}",
                popup_text=popup_content
            )

    # 5. Draw the route line
    draw_route(route_map, coordinates)

    # 6. Auto-fit zoom to show all points
    adjust_map_view(route_map, coordinates)

    # 7. Save the map
    save_map(route_map, output_path)

    print(f"✅ Carte générée avec succès : {output_path}")
    print(f"📍 {len(photo_points_sorted)} points tracés")
    
    return output_path