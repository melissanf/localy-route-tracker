import os

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


def ensure_output_folder(output_path="data/output"):
    """
    Ensures the output folder exists.
    If not, creates it.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
