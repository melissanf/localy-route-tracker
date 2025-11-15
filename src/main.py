# main.py

import os
from file_manager import get_images_from_folder, validate_image_count, ensure_output_folder
from image_handler import lire_exif, extraire_gps_brut
from gps_utils import convertir_gps
from map_plotter import generate_itinerary_map

def main():
    print("=== Application de Tracé d'Itinéraire à partir d'Images ===\n")

    # Step 1: Ask user to provide folder path
    folder_path = input("Entrez le chemin du dossier contenant vos images : ").strip()
    if not os.path.exists(folder_path):
        print("Le dossier n'existe pas. Veuillez vérifier le chemin.")
        return

    # Step 2: Get image files
    images = get_images_from_folder(folder_path)
    try:
        validate_image_count(images)
    except ValueError as ve:
        print(ve)
        return

    print(f"\n{len(images)} images trouvées :")
    for i, img in enumerate(images):
        print(f"{i+1}. {img}")

    # Step 3: Extract GPS data from images
    photo_points = []
    for img_path in images:
        exif = lire_exif(img_path)
        gps_brut = extraire_gps_brut(exif)
        coords = convertir_gps(gps_brut) if gps_brut else None 

        if coords:
            lat, lon = coords
            photo_points.append({
                "filename": os.path.basename(img_path),
                "latitude": lat,
                "longitude": lon
            })
        else:
            print(f"⚠️  Pas de données GPS pour l'image : {os.path.basename(img_path)}")

    if len(photo_points) < 2:
        print("\nPas assez de points GPS pour générer un itinéraire. Au moins 2 sont requis.")
        return

    # Step 4: Ensure output folder exists
    ensure_output_folder("data/output")

    # Step 5: Generate map
    output_path = "data/output/route_map.html"
    generate_itinerary_map(photo_points, output_path)

    print("\n✅ Itinéraire généré avec succès ! Ouvrez le fichier HTML pour le visualiser.")

if __name__ == "__main__":
    main()
