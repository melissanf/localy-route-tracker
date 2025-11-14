import folium
import os

def initialize_map(center_coordinates, zoom_start=16):
    lat, lon = center_coordinates
    return folium.Map(location=[lat, lon], zoom_start=zoom_start)


def add_colored_marker(map_object, coordinate, marker_color, tooltip_text=""):
    """
    Add a colored marker without popup.
    marker_color: 'green', 'red', 'blue'
    """
    lat, lon = coordinate

    folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(color=marker_color),
        tooltip=tooltip_text
    ).add_to(map_object)


def draw_route(map_object, coordinates_list):
    folium.PolyLine(
        coordinates_list,
        weight=4,
        opacity=0.8
    ).add_to(map_object)


def adjust_map_view(map_object, coordinates_list):
    map_object.fit_bounds(coordinates_list)


def save_map(map_object, output_path):
    directory = os.path.dirname(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    map_object.save(output_path)


def generate_itinerary_map(photo_points, output_path="data/output/route_map.html"):

    if len(photo_points) == 0:
        print("Aucune donnée GPS trouvée. Impossible de générer la carte.")
        return None

    # 1. Sort chronologically
    photo_points_sorted = sorted(photo_points, key=lambda x: x.get("timestamp", ""))

    # 2. Extract coordinates
    coordinates = [
        [p["latitude"], p["longitude"]]
        for p in photo_points_sorted
    ]

    # 3. Initialize map centered on first point
    first_point = coordinates[0]
    route_map = initialize_map(first_point)

    # 4. Add colored markers (no popups)
    for i, point in enumerate(photo_points_sorted):
        coord = (point["latitude"], point["longitude"])
        filename = point.get("filename", "")

        # First point = green
        if i == 0:
            add_colored_marker(route_map, coord, "green", tooltip_text=f"Start: {filename}")

        # Last point = red
        elif i == len(photo_points_sorted) - 1:
            add_colored_marker(route_map, coord, "red", tooltip_text=f"End: {filename}")

        # Middle points = blue
        else:
            add_colored_marker(route_map, coord, "blue", tooltip_text=filename)

    # 5. Draw the route
    draw_route(route_map, coordinates)

    # 6. Auto-fit zoom
    adjust_map_view(route_map, coordinates)

    # 7. Save
    save_map(route_map, output_path)

    print(f"Carte générée avec succès : {output_path}")
    return output_path
