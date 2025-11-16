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


def generate_static_map_image(photo_points, output_path="data/output/map_preview.png"):
    """
    Generate a static PNG image preview of the map with real map tiles.
    Uses staticmap library to fetch real OpenStreetMap tiles.
    """
    try:
        from staticmap import StaticMap, CircleMarker, Line
        
        # Sort by timestamp
        sorted_points = sorted(photo_points, key=lambda x: x.get("timestamp", "") or "")
        
        if len(sorted_points) < 2:
            return None
        
        # Create static map (800x600)
        m = StaticMap(800, 600, url_template='http://a.tile.openstreetmap.org/{z}/{x}/{y}.png')
        
        # Prepare coordinates for the route line
        line_coords = []
        
        # Add markers and collect coordinates
        for i, point in enumerate(sorted_points):
            lon = point["longitude"]
            lat = point["latitude"]
            line_coords.append((lon, lat))
            
            # Add colored markers
            if i == 0:
                # Start point - green
                marker = CircleMarker((lon, lat), '#10b981', 18)
                m.add_marker(marker)
            elif i == len(sorted_points) - 1:
                # End point - red
                marker = CircleMarker((lon, lat), '#ef4444', 18)
                m.add_marker(marker)
            else:
                # Middle points - blue
                marker = CircleMarker((lon, lat), '#3b82f6', 14)
                m.add_marker(marker)
        
        # Add route line
        line = Line(line_coords, '#173DED', 4)
        m.add_line(line)
        
        # Render and save
        image = m.render()
        
        # Save image
        directory = os.path.dirname(output_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        image.save(output_path)
        print(f"✅ Aperçu de carte généré avec vraie carte : {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"⚠️  Erreur lors de la génération de l'aperçu avec staticmap: {e}")
        print("Tentative avec méthode de secours...")
        import traceback
        traceback.print_exc()
        
        # Fallback to simple drawing if staticmap fails
        return generate_simple_map_image(photo_points, output_path)


def generate_simple_map_image(photo_points, output_path="data/output/map_preview.png"):
    """
    Fallback: Generate a simple map image without real tiles.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import math
        
        # Image dimensions
        width, height = 800, 600
        
        # Create white background
        img = Image.new('RGB', (width, height), '#f3f4f6')
        draw = ImageDraw.Draw(img)
        
        # Sort by timestamp
        sorted_points = sorted(photo_points, key=lambda x: x.get("timestamp", "") or "")
        
        if len(sorted_points) < 2:
            return None
        
        # Get coordinate bounds
        lats = [p["latitude"] for p in sorted_points]
        lons = [p["longitude"] for p in sorted_points]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Add padding (10%)
        lat_range = max_lat - min_lat or 0.01
        lon_range = max_lon - min_lon or 0.01
        
        min_lat -= lat_range * 0.1
        max_lat += lat_range * 0.1
        min_lon -= lon_range * 0.1
        max_lon += lon_range * 0.1
        
        # Map coordinates to image pixels
        padding = 60
        drawable_width = width - 2 * padding
        drawable_height = height - 2 * padding
        
        def lat_lon_to_xy(lat, lon):
            x = padding + ((lon - min_lon) / (max_lon - min_lon)) * drawable_width
            y = padding + ((max_lat - lat) / (max_lat - min_lat)) * drawable_height
            return int(x), int(y)
        
        # Convert all points
        pixel_points = [lat_lon_to_xy(p["latitude"], p["longitude"]) for p in sorted_points]
        
        # Draw route line
        if len(pixel_points) > 1:
            draw.line(pixel_points, fill='#173DED', width=4)
        
        # Draw markers with glow effect
        for i, (x, y) in enumerate(pixel_points):
            # Marker circle with shadow/glow
            radius = 14
            
            # Draw glow (larger semi-transparent circle)
            glow_radius = radius + 4
            
            if i == 0:
                # Start point - green with glow
                draw.ellipse([x-glow_radius, y-glow_radius, x+glow_radius, y+glow_radius], 
                           fill='#6ee7b7', outline=None)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           fill='#10b981', outline='white', width=3)
            elif i == len(pixel_points) - 1:
                # End point - red with glow
                draw.ellipse([x-glow_radius, y-glow_radius, x+glow_radius, y+glow_radius], 
                           fill='#fca5a5', outline=None)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           fill='#ef4444', outline='white', width=3)
            else:
                # Middle points - blue with glow
                draw.ellipse([x-glow_radius, y-glow_radius, x+glow_radius, y+glow_radius], 
                           fill='#93c5fd', outline=None)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           fill='#3b82f6', outline='white', width=3)
            
            # Point number
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()
            
            text = str(i + 1)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((x - text_width//2, y - text_height//2), text, 
                     fill='white', font=font)
        
        # Add title
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
        
        title = "Votre Itinéraire"
        draw.text((20, 20), title, fill='#1f2937', font=title_font)
        
        # Add legend
        legend_y = height - 40
        legend_items = [
            ('#10b981', 'Départ'),
            ('#3b82f6', 'Points'),
            ('#ef4444', 'Arrivée')
        ]
        
        legend_x = 20
        for color, label in legend_items:
            # Color circle
            draw.ellipse([legend_x, legend_y, legend_x+15, legend_y+15], 
                        fill=color, outline='white', width=2)
            # Label
            try:
                legend_font = ImageFont.truetype("arial.ttf", 12)
            except:
                legend_font = ImageFont.load_default()
            draw.text((legend_x + 20, legend_y), label, fill='#6b7280', font=legend_font)
            legend_x += 100
        
        # Save image
        directory = os.path.dirname(output_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        img.save(output_path, 'PNG')
        print(f"✅ Aperçu de carte généré : {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"⚠️  Erreur lors de la génération de l'aperçu: {e}")
        import traceback
        traceback.print_exc()
        return None