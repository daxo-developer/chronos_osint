import cv2
import numpy as np
from modules.streetview_matcher import match_with_panoramas

def detect_objects(image_path):
    # Загружаем предобученную модель YOLO (требует файлов .weights и .cfg)
    return []

def compare_with_streetview(objects, candidate_coords):
    matches = []
    for coord in candidate_coords:
        score = match_with_panoramas(coord, objects)
        matches.append({'coords': coord, 'score': score})
    return matches
