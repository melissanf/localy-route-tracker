import os
import shutil
from datetime import datetime

def get_images_from_paths(file_paths):
    """
    Returns a list of valid image file paths from a list of files/folders.
    Supports both individual files and folders.
    """
    valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".JPG", ".JPEG", ".PNG")
    images = []
    
    for path in file_paths:
        if os.path.isfile(path):
            # It's a file
            if path.lower().endswith(valid_extensions):
                images.append(path)
        elif os.path.isdir(path):
            # It's a folder - get all images from it
            for filename in os.listdir(path):
                if filename.lower().endswith(valid_extensions):
                    full_path = os.path.join(path, filename)
                    images.append(full_path)
    
    return images


def get_images_from_folder(folder_path):
    """
    Returns a list of valid image file paths (JPG/JPEG only)
    from the selected folder.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Le dossier n'existe pas : {folder_path}")

    valid_extensions = (".jpg", ".jpeg")
    images = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(valid_extensions):
            full_path = os.path.join(folder_path, filename)
            images.append(full_path)

    return images


def copy_images_to_data(image_paths, data_folder="data/images"):
    """
    Copies uploaded images to the data/images folder.
    Returns list of new paths in data folder.
    """
    ensure_output_folder(data_folder)
    
    copied_paths = []
    for img_path in image_paths:
        filename = os.path.basename(img_path)
        destination = os.path.join(data_folder, filename)
        
        # Avoid overwriting - add timestamp if file exists
        if os.path.exists(destination):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}{ext}"
            destination = os.path.join(data_folder, filename)
        
        shutil.copy2(img_path, destination)
        copied_paths.append(destination)
    
    return copied_paths


def validate_image_count(images_list, min_required=3):
    """
    Ensures the user has selected enough images.
    Raises an exception if not enough images.
    """
    if len(images_list) < min_required:
        raise ValueError(
            f"Vous devez sélectionner au moins {min_required} images. "
            f"Seulement {len(images_list)} détectées."
        )


def ensure_output_folder(output_path):
    """
    Ensures the output folder exists.
    If not, creates it.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)