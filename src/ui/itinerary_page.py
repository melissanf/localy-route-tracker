import customtkinter as ctk
import tkinterweb
import os
import sys
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_manager import get_images_from_paths, copy_images_to_data, ensure_output_folder
from image_handler import lire_exif, extraire_gps_brut, extraire_timestamp
from gps_utils import convertir_gps
from map_plotter import generate_itinerary_map

class ItineraryResultsApp:
    def __init__(self, root, file_paths, on_back_callback):
        self.root = root
        self.file_paths = file_paths
        self.on_back_callback = on_back_callback
        self.map_path = None
        self.setup_ui()
        # Start processing in background
        self.process_images()
        
    def setup_ui(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Separator line at top
        separator = ctk.CTkFrame(self.root, fg_color="#e5e7eb", height=2)
        separator.pack(fill="x", padx=20, pady=(15, 15))
        
        # Header
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Title
        title_label = ctk.CTkLabel(header_frame, text="Votre Itinéraire Personnalisé", 
                                  font=("Arial", 20, "bold"), text_color="#1f2937", 
                                  anchor="w")
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(header_frame, 
                                     text="Basé sur vos photos téléchargées, voici votre itinéraire suggéré", 
                                     font=("Arial", 10), text_color="#6b7280", anchor="w")
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Map section with heading
        map_header = ctk.CTkFrame(self.root, fg_color="transparent")
        map_header.pack(fill="x", padx=20, pady=(0, 10))
        
        map_title = ctk.CTkLabel(map_header, text="Votre Itinéraire", 
                                 font=("Arial", 16, "bold"), text_color="#1f2937")
        map_title.pack(anchor="w")
        
        # Map container
        self.map_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.map_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Loading placeholder
        self.loading_frame = ctk.CTkFrame(self.map_container, fg_color="#f3f4f6", 
                                          border_width=2, border_color="#d1d5db", 
                                          corner_radius=12)
        self.loading_frame.pack(fill="both", expand=True)
        
        # Loading content
        loading_content = ctk.CTkFrame(self.loading_frame, fg_color="transparent")
        loading_content.place(relx=0.5, rely=0.5, anchor="center")
        
        self.loading_label = ctk.CTkLabel(loading_content, text="⏳ Génération de la carte...", 
                                         font=("Arial", 14, "bold"), 
                                         text_color="#6b7280", fg_color="transparent")
        self.loading_label.pack()
        
        self.status_label = ctk.CTkLabel(loading_content, text="Traitement des images...", 
                                        font=("Arial", 10), text_color="#9ca3af",
                                        fg_color="transparent")
        self.status_label.pack(pady=(5, 0))
        
        # Action buttons at bottom
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Exit button (back to upload)
        exit_btn = ctk.CTkButton(button_frame, text="Retour", 
                                font=("Arial", 11, "bold"), fg_color="#173DED", 
                                text_color="white", border_width=0,
                                hover_color="#0F2DB8", corner_radius=12, height=40, 
                                cursor="hand2", command=self.go_back_to_upload)
        exit_btn.pack()
    
    def process_images(self):
        """Process images in background thread"""
        def process():
            try:
                # Update status
                self.root.after(0, lambda: self.status_label.configure(
                    text="Extraction des données GPS..."))
                
                # Get valid images from paths
                images = get_images_from_paths(self.file_paths)
                
                if len(images) < 3:
                    self.root.after(0, lambda: self.show_error(
                        "Pas assez d'images valides trouvées (minimum 3)"))
                    return
                
                # Copy images to data folder
                ensure_output_folder("data/images")
                copied_images = copy_images_to_data(images, "data/images")
                
                # Extract GPS data with timestamps
                photo_points = []
                for img_path in copied_images:
                    exif = lire_exif(img_path)
                    gps_brut = extraire_gps_brut(exif)
                    coords = convertir_gps(gps_brut) if gps_brut else None
                    timestamp = extraire_timestamp(exif)
                    
                    if coords:
                        lat, lon = coords
                        photo_points.append({
                            "filename": os.path.basename(img_path),
                            "latitude": lat,
                            "longitude": lon,
                            "timestamp": timestamp.isoformat() if timestamp else ""
                        })
                
                if len(photo_points) < 2:
                    self.root.after(0, lambda: self.show_error(
                        "Pas assez de données GPS trouvées dans les images (minimum 2)"))
                    return
                
                # Update status
                self.root.after(0, lambda: self.status_label.configure(
                    text="Génération de la carte..."))
                
                # Generate map
                ensure_output_folder("data/output")
                map_path = generate_itinerary_map(photo_points, "data/output/route_map.html")
                
                # Display map
                self.root.after(0, lambda: self.display_map(map_path))
                
            except Exception as e:
                error_msg = f"Erreur lors du traitement: {str(e)}"
                self.root.after(0, lambda: self.show_error(error_msg))
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def display_map(self, map_path):
        """Display the generated map"""
        try:
            # Remove loading frame
            self.loading_frame.destroy()
            
            # Create HTML frame to display map
            map_frame = tkinterweb.HtmlFrame(self.map_container, messages_enabled=False)
            map_frame.pack(fill="both", expand=True)
            
            # Load the map HTML file
            map_frame.load_file(os.path.abspath(map_path))
            
            self.map_path = map_path
            
        except Exception as e:
            self.show_error(f"Erreur d'affichage de la carte: {str(e)}")
    
    def show_error(self, message):
        """Show error message"""
        # Clear loading content
        for widget in self.loading_frame.winfo_children():
            widget.destroy()
        
        # Show error
        error_content = ctk.CTkFrame(self.loading_frame, fg_color="transparent")
        error_content.place(relx=0.5, rely=0.5, anchor="center")
        
        error_icon = ctk.CTkLabel(error_content, text="⚠️", 
                                 font=("Arial", 32), text_color="#dc2626",
                                 fg_color="transparent")
        error_icon.pack()
        
        error_label = ctk.CTkLabel(error_content, text=message, 
                                  font=("Arial", 12), text_color="#dc2626",
                                  fg_color="transparent", wraplength=400)
        error_label.pack(pady=(10, 0))
    
    def go_back_to_upload(self):
        """Return to upload photos page"""
        if self.on_back_callback:
            self.on_back_callback()