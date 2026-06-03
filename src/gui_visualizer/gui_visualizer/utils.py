import colorsys

from PyQt5.QtGui import QColor

def vehicle_color(vehicle_id: int) -> QColor:
    # Deterministic bright colour per vehicle ID
    hue = (vehicle_id * 0.618033988749895) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 0.95)
    return QColor(int(r * 255), int(g * 255), int(b * 255))