from PIL import Image, ExifTags
from datetime import datetime

def lire_exif(chemin_image):
    """Read EXIF data from an image"""
    try:
        img = Image.open(chemin_image)
        exif = {}
        infos = img._getexif()
        if infos:
            for tag, valeur in infos.items():
                nom_tag = ExifTags.TAGS.get(tag, tag)
                exif[nom_tag] = valeur
        return exif
    except Exception as e:
        print(f"Erreur lors de la lecture EXIF de {chemin_image}: {e}")
        return {}


def extraire_gps_brut(exif):
    """Extract raw GPS data from EXIF"""
    gps_info = exif.get('GPSInfo')
    if not gps_info:
        return None

    gps = {}
    for k, v in gps_info.items():
        nom = ExifTags.GPSTAGS.get(k, k)
        gps[nom] = v

    # return raw DMS data
    try:
        return {
            "lat": gps['GPSLatitude'],
            "lat_ref": gps['GPSLatitudeRef'],
            "lon": gps['GPSLongitude'],
            "lon_ref": gps['GPSLongitudeRef']
        }
    except KeyError:
        return None


def extraire_timestamp(exif):
    """Extract timestamp from EXIF data"""
    # Try different datetime tags
    datetime_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
    
    for tag in datetime_tags:
        if tag in exif:
            try:
                dt_str = exif[tag]
                # EXIF datetime format: "YYYY:MM:DD HH:MM:SS"
                dt = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                return dt
            except Exception:
                continue
    
    return None