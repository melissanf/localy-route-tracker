import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import time

class PhotoUploadApp:
    def __init__(self, root, on_submit_callback):
        self.root = root
        self.on_submit_callback = on_submit_callback
        self.uploaded_files = []
        self.file_widgets = []
        self.error_frame = None
        self.setup_ui()
        
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
        
        # Title and subtitle container
        text_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_frame.pack(anchor="w")
        
        title_label = ctk.CTkLabel(text_frame, text="Télécharger des Photos", 
                                  font=("Arial", 18, "bold"), text_color="#1f2937", 
                                  anchor="w")
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(text_frame, 
                                     text="Sélectionnez et téléchargez les photos de votre choix (minimum 3 photos)", 
                                     font=("Arial", 10), text_color="#6b7280", anchor="w")
        subtitle_label.pack(anchor="w")
        
        # Upload area (smaller) with more rounded corners
        upload_container = ctk.CTkFrame(self.root, fg_color="transparent")
        upload_container.pack(fill="x", padx=40, pady=(15, 15))
        
        upload_frame = ctk.CTkFrame(upload_container, fg_color="white", border_width=2, 
                                   border_color="#d1d5db", corner_radius=16)
        upload_frame.pack(fill="x", ipady=25)
        
        # CENTERED UPLOAD BUTTON AND TEXT
        center_frame = ctk.CTkFrame(upload_frame, fg_color="white")
        center_frame.pack(expand=True, pady=15)
        
        # Upload button - centered with more rounded corners
        upload_btn = ctk.CTkButton(center_frame, text="⬆  Télécharger", font=("Arial", 11),
                                  fg_color="white", text_color="#374151", border_width=1,
                                  border_color="#d1d5db", hover_color="#f9fafb",
                                  corner_radius=12, height=40, cursor="hand2",
                                  command=self.select_files)
        upload_btn.pack(pady=(0, 8))
        
        # Instructions - centered
        instruction_label = ctk.CTkLabel(center_frame, text="Choisissez des fichiers ou cliquez sur le bouton Télécharger", 
                                        font=("Arial", 11), text_color="#374151", fg_color="white")
        instruction_label.pack(pady=2)
        
        size_label = ctk.CTkLabel(center_frame, text="Taille maximale de fichier 500 Mo", 
                                 font=("Arial", 9), text_color="#9ca3af", fg_color="white")
        size_label.pack(pady=(2, 0))
        
        # Files list container with scrollbar
        list_container = ctk.CTkFrame(self.root, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Error frame (initially hidden) with more rounded corners
        self.error_frame = ctk.CTkFrame(self.root, fg_color="#fee2e2", border_width=1, 
                                       border_color="#fecaca", corner_radius=12)
        
        error_content = ctk.CTkFrame(self.error_frame, fg_color="transparent")
        error_content.pack(fill="x", padx=15, pady=8)
        
        error_icon = ctk.CTkLabel(error_content, text="⚠", font=("Arial", 16), 
                                 text_color="#dc2626", fg_color="transparent")
        error_icon.pack(side="left", padx=(0, 10))
        
        self.error_label = ctk.CTkLabel(error_content, text="", font=("Arial", 11), 
                                       text_color="#dc2626", fg_color="transparent")
        self.error_label.pack(side="left", fill="x", expand=True)
        
        # Submit button at bottom with more rounded corners
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.submit_btn = ctk.CTkButton(button_frame, text="Soumettre les Photos", 
                                       font=("Arial", 11, "bold"), fg_color="#173DED", 
                                       text_color="white", hover_color="#0F2DB8",
                                       corner_radius=12, height=40, cursor="hand2",
                                       command=self.submit_photos)
        self.submit_btn.pack()
        
    def select_files(self):
        """Open file dialog to select multiple image files"""
        filetypes = [
            ("Fichiers image", "*.jpg *.jpeg *.png *.gif *.bmp *.JPG *.JPEG *.PNG"),
            ("Tous les fichiers", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Sélectionner des Photos",
            filetypes=filetypes
        )
        
        if files:
            for file_path in files:
                if file_path not in [f['path'] for f in self.uploaded_files]:
                    self.add_file(file_path)
    
    def add_file(self, file_path):
        """Add a file to the upload list"""
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Check file size (500 MB limit)
            if file_size > 500 * 1024 * 1024:
                messagebox.showwarning("Fichier Trop Volumineux", 
                                      f"{file_name} dépasse la limite de 500 Mo.")
                return
            
            file_info = {
                'path': file_path,
                'name': file_name,
                'size': file_size,
                'status': 'uploading',
                'progress_value': 0
            }
            
            self.uploaded_files.append(file_info)
            self.create_file_widget(file_info)
            
            # Hide error frame when adding files
            self.hide_error()
            
            # Simulate upload
            self.simulate_upload(file_info)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'ajout du fichier: {str(e)}")
    
    def create_file_widget(self, file_info):
        """Create a widget for each uploaded file (smaller frames) with more rounded corners"""
        file_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white", border_width=1, 
                                 border_color="#e5e7eb", corner_radius=12, height=70)
        file_frame.pack(fill="x", pady=3, padx=5)
        file_frame.pack_propagate(False)
        
        # Main content frame
        content_frame = ctk.CTkFrame(file_frame, fg_color="white")
        content_frame.pack(fill="x", padx=12, pady=8)
        
        # File icon
        icon_label = ctk.CTkLabel(content_frame, text="📄", font=("Arial", 20),
                                 fg_color="transparent", text_color="#1f2937")
        icon_label.pack(side="left", padx=(0, 10))
        
        # File details
        details_frame = ctk.CTkFrame(content_frame, fg_color="white")
        details_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(details_frame, text=file_info['name'], 
                                 font=("Arial", 10, "bold"), text_color="#1f2937",
                                 fg_color="white", anchor="w")
        name_label.pack(fill="x")
        
        # Size and status frame
        status_frame = ctk.CTkFrame(details_frame, fg_color="white")
        status_frame.pack(fill="x", pady=(1, 0))
        
        size_str = self.format_file_size(file_info['size'])
        size_label = ctk.CTkLabel(status_frame, text=f"0 Ko / {size_str}", 
                                 font=("Arial", 8), text_color="#6b7280", fg_color="white")
        size_label.pack(side="left")
        
        status_label = ctk.CTkLabel(status_frame, text="  •  Téléchargement...", 
                                   font=("Arial", 8), text_color="#f59e0b", fg_color="white")
        status_label.pack(side="left")
        
        # Delete button with more rounded corners
        delete_btn = ctk.CTkButton(content_frame, text="🗑", font=("Arial", 14),
                                  width=28, height=28, fg_color="white", hover_color="#f3f4f6",
                                  text_color="#9ca3af", corner_radius=20, cursor="hand2",
                                  command=lambda: self.remove_file(file_info, file_frame))
        delete_btn.pack(side="right")
        
        # Progress bar frame
        progress_frame = ctk.CTkFrame(file_frame, fg_color="white")
        progress_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        # Progress bar with more rounded corners
        progress_bar = ctk.CTkProgressBar(progress_frame, height=4, fg_color="#e5e7eb",
                                         progress_color="#173DED", corner_radius=8)
        progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        progress_bar.set(0)
        
        # Percentage label
        percentage_label = ctk.CTkLabel(progress_frame, text="0%", 
                                       font=("Arial", 8, "bold"), text_color="#6b7280",
                                       fg_color="white")
        percentage_label.pack(side="left")
        
        # Store references
        file_info['widget'] = file_frame
        file_info['progress_bar'] = progress_bar
        file_info['status_label'] = status_label
        file_info['size_label'] = size_label
        file_info['percentage_label'] = percentage_label
        
        self.file_widgets.append(file_frame)
    
    def simulate_upload(self, file_info):
        """Simulate file upload with progress"""
        def upload():
            try:
                for i in range(101):
                    if file_info['status'] == 'removed':
                        return
                    
                    time.sleep(0.03)
                    
                    # Update progress bar
                    file_info['progress_bar'].set(i / 100)
                    
                    # Update percentage
                    file_info['percentage_label'].configure(text=f"{i}%")
                    
                    # Update size
                    current_size = (file_info['size'] * i) / 100
                    total_size = file_info['size']
                    file_info['size_label'].configure(
                        text=f"{self.format_file_size(current_size)} / {self.format_file_size(total_size)}"
                    )
                    
                    if i == 100:
                        file_info['status'] = 'completed'
                        file_info['status_label'].configure(text="  •  Terminé", text_color="#10b981")
                        
            except Exception as e:
                print(f"Erreur de téléchargement: {e}")
        
        thread = threading.Thread(target=upload, daemon=True)
        thread.start()
    
    def remove_file(self, file_info, widget):
        """Remove a file from the upload list"""
        file_info['status'] = 'removed'
        widget.destroy()
        if file_info in self.uploaded_files:
            self.uploaded_files.remove(file_info)
        if widget in self.file_widgets:
            self.file_widgets.remove(widget)
        # Hide error when removing files
        self.hide_error()
    
    def show_error(self, message):
        """Show error frame with message"""
        self.error_label.configure(text=message)
        # Make sure error frame is packed in the correct position
        if not self.error_frame.winfo_ismapped():
            self.error_frame.pack(fill="x", padx=20, pady=(0, 10), before=self.submit_btn.master)
        self.root.update()
    
    def hide_error(self):
        """Hide error frame"""
        if self.error_frame.winfo_ismapped():
            self.error_frame.pack_forget()
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.0f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.0f} To"
    
    def submit_photos(self):
        """Handle photo submission - check for minimum 3 photos"""
        # Count completed files
        completed_files = [f for f in self.uploaded_files if f.get('status') == 'completed']
        
        print(f"Debug: Total des fichiers téléchargés: {len(self.uploaded_files)}")
        print(f"Debug: Fichiers terminés: {len(completed_files)}")
        
        if len(completed_files) < 3:
            # Show error frame
            self.show_error("Veuillez télécharger au moins 3 photos avant de soumettre.")
            return
        
        # Hide error if validation passes
        self.hide_error()
        
        # Get file paths
        file_paths = [f['path'] for f in completed_files]
        
        print("Fichiers téléchargés:")
        for path in file_paths:
            print(f"  - {path}")
        
        # Navigate to itinerary page
        if self.on_submit_callback:
            self.on_submit_callback(file_paths)