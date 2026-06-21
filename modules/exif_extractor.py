import exifread
import io
from PIL import Image
import re
from datetime import datetime

def extract_gps(image_path):
    # 1. Основной EXIF
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
    gps = {}
    for tag, value in tags.items():
        if tag.startswith('GPS'):
            gps[tag] = str(value)
    if 'GPS GPSLatitude' in gps and 'GPS GPSLongitude' in gps:
        lat = convert_to_degrees(gps['GPS GPSLatitude'])
        lon = convert_to_degrees(gps['GPS GPSLongitude'])
        return (lat, lon)

    # 2. Попытка извлечь из Thumbnail (если мессенджер сжал, но оставил миниатюру)
    try:
        img = Image.open(image_path)
        if 'thumbnail' in img.info:
            thumb_data = img.info['thumbnail']
            thumb_tags = exifread.process_file(io.BytesIO(thumb_data), details=False)
            gps_thumb = {}
            for tag, value in thumb_tags.items():
                if tag.startswith('GPS'):
                    gps_thumb[tag] = str(value)
            if 'GPS GPSLatitude' in gps_thumb and 'GPS GPSLongitude' in gps_thumb:
                lat = convert_to_degrees(gps_thumb['GPS GPSLatitude'])
                lon = convert_to_degrees(gps_thumb['GPS GPSLongitude'])
                return (lat, lon)
    except Exception:
        pass
    return None

def convert_to_degrees(value):
    parts = re.findall(r'(\d+)/(\d+)', value)
    deg = float(parts[0][0]) / float(parts[0][1])
    if len(parts) > 1:
        deg += float(parts[1][0]) / float(parts[1][1]) / 60.0
    if len(parts) > 2:
        deg += float(parts[2][0]) / float(parts[2][1]) / 3600.0
    return deg

def extract_datetime(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
    for tag, value in tags.items():
        if tag == 'EXIF DateTimeOriginal' or tag == 'Image DateTime':
            return datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
    return None
