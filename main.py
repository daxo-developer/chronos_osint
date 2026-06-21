import sys
import json
from modules.exif_extractor import extract_gps
from modules.visual_search import search_all_engines
from modules.scene_analyzer import detect_objects, compare_with_streetview
from modules.shadow_geo import estimate_location_by_shadow
from modules.satellite import fetch_satellite_images
from modules.utils import load_config

def extract_geo_from_page(url):
    # Парсинг страницы на предмет координат
    return None

def geo_locate(image_path):
    # 1. Проверка EXIF
    coords = extract_gps(image_path)
    if coords:
        return {"coords": coords, "method": "exif", "confidence": 100}

    # 2. Визуальный поиск по картинкам
    search_results = search_all_engines(image_path)
    candidate_coords = []
    for url in search_results:
        c = extract_geo_from_page(url)
        if c:
            candidate_coords.append(c)

    # 3. Анализ сцены и сравнение с панорамами
    objects = detect_objects(image_path)
    streetview_matches = compare_with_streetview(objects, candidate_coords)
    if streetview_matches:
        best = max(streetview_matches, key=lambda x: x['score'])
        return {"coords": best['coords'], "method": "streetview", "confidence": best['score']}

    # 4. Расчёт по тени
    shadow_est = estimate_location_by_shadow(image_path)
    if shadow_est:
        sat_coords = fetch_satellite_images(shadow_est)
        if sat_coords:
            return {"coords": sat_coords, "method": "shadow+satellite", "confidence": 75}

    # 5. Агрегация всех найденных координат
    if candidate_coords:
        avg_lat = sum(c[0] for c in candidate_coords) / len(candidate_coords)
        avg_lon = sum(c[1] for c in candidate_coords) / len(candidate_coords)
        return {"coords": (avg_lat, avg_lon), "method": "aggregated", "confidence": 40}

    return {"coords": None, "error": "Не удалось определить локацию"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
        sys.exit(1)
    result = geo_locate(sys.argv[1])
    print(json.dumps(result, indent=2))
