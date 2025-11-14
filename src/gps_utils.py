def to_float(x):
    try:
        return float(x[0]) / float(x[1])
    except TypeError:
        return float(x)


def en_degres(val):
    d = to_float(val[0])
    m = to_float(val[1])
    s = to_float(val[2])
    return d + (m / 60) + (s / 3600)


def convertir_gps(gps_brut):
    try:
        lat = en_degres(gps_brut["lat"])
        if gps_brut["lat_ref"] != 'N':
            lat = -lat

        lon = en_degres(gps_brut["lon"])
        if gps_brut["lon_ref"] != 'E':
            lon = -lon

        return lat, lon

    except Exception:
        return None
