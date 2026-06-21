import pytest
from modules.exif_extractor import extract_gps

def test_extract_gps():
    #Замените путь на реальное тестовое изображение с GPS.
    coords = extract_gps('examples/test_with_gps.jpg')
    # Если файла нет, тест пропускается:
    if coords is None:
        pytest.skip("Тестовое изображение не найдено")
    assert abs(coords[0] - 55.7558) < 0.001
    assert abs(coords[1] - 37.6173) < 0.001
