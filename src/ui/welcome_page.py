import customtkinter as ctk

class WelcomeApp:
    def __init__(self, root, on_start_callback):
        self.root = root
        self.on_start_callback = on_start_callback
        self.setup_ui()
        
    def setup_ui(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container - centered content
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Center frame
        center_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Welcome title
        welcome_title = ctk.CTkLabel(center_frame, text="Bienvenue sur Localy", 
                                    font=("Arial", 32, "bold"), text_color="#1f2937")
        welcome_title.pack(pady=(0, 15))
        
        # Description
        description_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        description_frame.pack(pady=(0, 30))
        
        description_text = """Bienvenue dans notre application pour tracer vos itinéraires
à partir de photos ! Prenez des photos à différents endroits,
puis importez-les dans l'application. Nous récupérerons
automatiquement les informations importantes de vos photos
pour créer et afficher votre itinéraire."""
        
        description_label = ctk.CTkLabel(description_frame, text=description_text,
                                        font=("Arial", 13), text_color="#6b7280",
                                        justify="center")
        description_label.pack()
        
        # CTA Button
        cta_button = ctk.CTkButton(center_frame, text="Commencer",
                                  font=("Arial", 14, "bold"), fg_color="#173DED",
                                  text_color="white", hover_color="#0F2DB8",
                                  corner_radius=12, height=50, width=200,
                                  cursor="hand2", command=self.get_started)
        cta_button.pack(pady=(10, 0))
        
    def get_started(self):
        """Navigate to upload photos page"""
        if self.on_start_callback:
            self.on_start_callback()