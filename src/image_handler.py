from PIL import Image, ExifTags

def lire_exif(chemin_image):
    img = Image.open(chemin_image)
    exif = {}
    infos = img._getexif()
    if infos:
        for tag, valeur in infos.items():
            nom_tag = ExifTags.TAGS.get(tag, tag)
            exif[nom_tag] = valeur
    return exif


def extraire_gps_brut(exif):
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
