import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
import threading
import webbrowser

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
        self.photo_points = []
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
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Exit button (back to upload)
        exit_btn = ctk.CTkButton(self.button_frame, text="Retour", 
                                font=("Arial", 11, "bold"), fg_color="#6b7280", 
                                text_color="white", border_width=0,
                                hover_color="#4b5563", corner_radius=12, height=40, 
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
                for img_path in copied_images:
                    exif = lire_exif(img_path)
                    gps_brut = extraire_gps_brut(exif)
                    coords = convertir_gps(gps_brut) if gps_brut else None
                    timestamp = extraire_timestamp(exif)
                    
                    if coords:
                        lat, lon = coords
                        self.photo_points.append({
                            "filename": os.path.basename(img_path),
                            "latitude": lat,
                            "longitude": lon,
                            "timestamp": timestamp.isoformat() if timestamp else ""
                        })
                
                if len(self.photo_points) < 2:
                    self.root.after(0, lambda: self.show_error(
                        "Pas assez de données GPS trouvées dans les images (minimum 2)"))
                    return
                
                # Update status
                self.root.after(0, lambda: self.status_label.configure(
                    text="Génération de la carte..."))
                
                # Generate map
                ensure_output_folder("data/output")
                map_path = generate_itinerary_map(self.photo_points, "data/output/route_map.html")
                
                # Display map summary
                self.root.after(0, lambda: self.display_map_summary(map_path))
                
            except Exception as e:
                error_msg = f"Erreur lors du traitement: {str(e)}"
                self.root.after(0, lambda: self.show_error(error_msg))
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def display_map_summary(self, map_path):
        """Display map summary with icon and open button"""
        try:
            # Remove loading frame
            self.loading_frame.destroy()
            
            # Create summary frame
            summary_frame = ctk.CTkFrame(self.map_container, fg_color="white", 
                                        border_width=2, border_color="#d1d5db", 
                                        corner_radius=12)
            summary_frame.pack(fill="both", expand=True)
            
            # Center content
            content_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
            content_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # Map icon
            map_icon = ctk.CTkLabel(content_frame, text="🗺️", 
                                   font=("Arial", 64), fg_color="transparent")
            map_icon.pack(pady=(0, 15))
            
            # Success message
            success_label = ctk.CTkLabel(content_frame, 
                                        text="Carte Générée avec Succès!", 
                                        font=("Arial", 18, "bold"), 
                                        text_color="#10b981", fg_color="transparent")
            success_label.pack(pady=(0, 5))
            
            # Stats
            stats_text = f"📍 {len(self.photo_points)} points tracés sur votre itinéraire"
            stats_label = ctk.CTkLabel(content_frame, text=stats_text, 
                                      font=("Arial", 12), text_color="#6b7280",
                                      fg_color="transparent")
            stats_label.pack(pady=(0, 20))
            
            # Open map button
            open_btn = ctk.CTkButton(content_frame, 
                                    text="🌐  Ouvrir la Carte Interactive", 
                                    font=("Arial", 13, "bold"), 
                                    fg_color="#173DED", text_color="white",
                                    hover_color="#0F2DB8", corner_radius=12, 
                                    height=50, width=280, cursor="hand2",
                                    command=lambda: self.open_map_in_browser(map_path))
            open_btn.pack()
            
            # Info text
            info_label = ctk.CTkLabel(content_frame, 
                                     text="La carte s'ouvrira dans votre navigateur par défaut", 
                                     font=("Arial", 9), text_color="#9ca3af",
                                     fg_color="transparent")
            info_label.pack(pady=(8, 0))
            
            self.map_path = map_path
            
            # Update button frame - add "Open Map" button
            for widget in self.button_frame.winfo_children():
                widget.destroy()
            
            # Button container for side-by-side buttons
            btn_container = ctk.CTkFrame(self.button_frame, fg_color="transparent")
            btn_container.pack()
            
            # Back button
            back_btn = ctk.CTkButton(btn_container, text="Retour", 
                                    font=("Arial", 11, "bold"), 
                                    fg_color="#6b7280", text_color="white",
                                    hover_color="#4b5563", corner_radius=12, 
                                    height=40, width=150, cursor="hand2",
                                    command=self.go_back_to_upload)
            back_btn.pack(side="left", padx=5)
            
            # Open map button (also in bottom)
            open_btn2 = ctk.CTkButton(btn_container, text="Ouvrir la Carte", 
                                     font=("Arial", 11, "bold"), 
                                     fg_color="#173DED", text_color="white",
                                     hover_color="#0F2DB8", corner_radius=12, 
                                     height=40, width=150, cursor="hand2",
                                     command=lambda: self.open_map_in_browser(map_path))
            open_btn2.pack(side="left", padx=5)
            
        except Exception as e:
            self.show_error(f"Erreur d'affichage: {str(e)}")
    
    def open_map_in_browser(self, map_path):
        """Open the map HTML file in default browser"""
        try:
            abs_path = os.path.abspath(map_path)
            webbrowser.open('file://' + abs_path)
        except Exception as e:
            print(f"Erreur lors de l'ouverture du navigateur: {e}")
    
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