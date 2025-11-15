import customtkinter as ctk
import sys
import os
from tkinterweb import HtmlFrame

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.welcome_page import WelcomeApp
from ui.upload_page import PhotoUploadApp
from ui.itinerary_page import ItineraryResultsApp

class LocalyApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Localy")
        self.root.geometry("700x650")
        
        # Configure appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Start with welcome page
        self.show_welcome_page()
        
    def show_welcome_page(self):
        """Display the welcome page"""
        WelcomeApp(self.root, on_start_callback=self.show_upload_page)
    
    def show_upload_page(self):
        """Display the upload photos page"""
        PhotoUploadApp(self.root, on_submit_callback=self.show_itinerary_page)
    
    def show_itinerary_page(self, file_paths):
        """Display the itinerary results page"""
        ItineraryResultsApp(self.root, file_paths, on_back_callback=self.show_upload_page)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = LocalyApp()
    app.run()