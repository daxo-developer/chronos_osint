import cv2
import math
from suncalc import get_position
from modules.exif_extractor import extract_datetime
import pytz
from datetime import datetime

def estimate_location_by_shadow(image_path, known_height=1.7, approx_time=None):
    """
    Оценивает координаты по тени.
    Возвращает (lat, lon) или None.
    Использует только направление тени (азимут) из-за отсутствия масштаба.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    shadow = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(shadow)
    angle_deg = rect[2]  # от -90 до 0
    if angle_deg < 0:
        angle_deg += 180

    if approx_time is None:
        approx_time = extract_datetime(image_path) or datetime.now(pytz.UTC)

    best_score = float('inf')
    best_coord = None
    # Грубый перебор по широте и долготе
    for lat in range(-90, 91, 2):
        for lon in range(-180, 181, 2):
            pos = get_position(approx_time, lon, lat)
            alt_deg = math.degrees(pos['altitude'])
            az_deg = math.degrees(pos['azimuth'])
            if alt_deg <= 0:
                continue
            # Направление тени (противоположно солнцу)
            shadow_az = (az_deg + 180) % 360
            # Симметричная разница (линия тени не имеет направления)
            diff = abs(shadow_az - angle_deg) % 180
            if diff > 90:
                diff = 180 - diff
            if diff < best_score:
                best_score = diff
                best_coord = (lat, lon)
    if best_coord and best_score < 20:  # допуск 20 градусов
        return best_coord
    return None
