"""Interactive 2-D top-down map widget that renders vehicle positions,
orientations, and trails using QPainter."""

import math
import time
from typing import Dict, Optional, Tuple

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QRadialGradient,
)
from PyQt5.QtWidgets import QWidget

from .data_model import VehicleState
from .utils import vehicle_color


class MapCanvas(QWidget):
    """Interactive 2-D top-down visualisation of vehicle positions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vehicles: Dict[int, VehicleState] = {}
        self.vehicle_timeout: float = 2.0

        # View transform
        self.scale: float = 300.0       # pixels per metre
        self.offset_x: float = 0.0      # world coord at widget centre
        self.offset_y: float = 0.0
        self._dragging: bool = False
        self._last_mouse: Optional[QPointF] = None

        # Display flags
        self.show_trails = True
        self.show_ids = True
        self.show_orientation = True
        self.show_grid = True

        self.setMinimumSize(500, 500)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    # ── Coordinate transforms ──────────────────────────────────────

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        sx = self.width() / 2.0 + (wx - self.offset_x) * self.scale
        sy = self.height() / 2.0 - (wy - self.offset_y) * self.scale
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        wx = (sx - self.width() / 2.0) / self.scale + self.offset_x
        wy = -(sy - self.height() / 2.0) / self.scale + self.offset_y
        return wx, wy

    # ── Public API ─────────────────────────────────────────────────

    def update_vehicles(self, vehicles: Dict[int, VehicleState]):
        self.vehicles = vehicles
        self.update()

    def reset_view(self):
        self.scale = 300.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.update()

    def fit_active_vehicles(self):
        active = [
            v
            for v in self.vehicles.values()
            if time.time() - v.last_seen < self.vehicle_timeout
        ]
        if not active:
            self.reset_view()
            return
        xs = [v.position_x for v in active]
        ys = [v.position_y for v in active]
        self.offset_x = (min(xs) + max(xs)) / 2.0
        self.offset_y = (min(ys) + max(ys)) / 2.0
        span_x = max(max(xs) - min(xs), 0.3) + 0.4
        span_y = max(max(ys) - min(ys), 0.3) + 0.4
        self.scale = min(self.width() / span_x, self.height() / span_y) * 0.8
        self.scale = max(10, min(8000, self.scale))
        self.update()

    # ── Painting ───────────────────────────────────────────────────

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(20, 22, 35))
        grad.setColorAt(1, QColor(30, 32, 48))
        p.fillRect(self.rect(), grad)

        if self.show_grid:
            self._paint_grid(p)
        self._paint_origin(p)

        now = time.time()
        for vid in sorted(self.vehicles):
            v = self.vehicles[vid]
            active = (now - v.last_seen) < self.vehicle_timeout
            if self.show_trails:
                self._paint_trail(p, v, active)
            self._paint_vehicle(p, v, active)

        self._paint_hud(p)
        p.end()

    # ── Sub-painters ───────────────────────────────────────────────

    def _paint_grid(self, p: QPainter):
        pen = QPen(QColor(50, 52, 68), 1, Qt.DotLine)
        label_pen = QPen(QColor(90, 92, 110))
        label_font = QFont("Consolas", 7)

        world_per_px = 1.0 / self.scale
        target = 80 * world_per_px
        mag = 10 ** math.floor(math.log10(max(target, 1e-9)))
        nice = [mag, 2 * mag, 5 * mag, 10 * mag]
        spacing = min(nice, key=lambda s: abs(s - target))

        wl, wt = self.screen_to_world(0, 0)
        wr, wb = self.screen_to_world(self.width(), self.height())

        x = math.floor(min(wl, wr) / spacing) * spacing
        while x <= max(wl, wr):
            sx, _ = self.world_to_screen(x, 0)
            p.setPen(pen)
            p.drawLine(int(sx), 0, int(sx), self.height())
            p.setPen(label_pen)
            p.setFont(label_font)
            p.drawText(int(sx) + 2, self.height() - 4, f"{x:g}")
            x += spacing

        y = math.floor(min(wb, wt) / spacing) * spacing
        while y <= max(wb, wt):
            _, sy = self.world_to_screen(0, y)
            p.setPen(pen)
            p.drawLine(0, int(sy), self.width(), int(sy))
            p.setPen(label_pen)
            p.setFont(label_font)
            p.drawText(3, int(sy) - 2, f"{y:g}")
            y += spacing

    def _paint_origin(self, p: QPainter):
        ox, oy = self.world_to_screen(0, 0)
        arm = 28

        p.setPen(QPen(QColor(255, 70, 70), 2))
        p.drawLine(int(ox), int(oy), int(ox + arm), int(oy))
        p.setFont(QFont("Consolas", 9, QFont.Bold))
        p.drawText(int(ox + arm + 3), int(oy + 5), "X")

        p.setPen(QPen(QColor(70, 255, 70), 2))
        p.drawLine(int(ox), int(oy), int(ox), int(oy - arm))
        p.drawText(int(ox + 3), int(oy - arm - 3), "Y")

    def _paint_trail(self, p: QPainter, v: VehicleState, active: bool):
        color = vehicle_color(v.vehicle_id)
        trail = list(v.trail)
        n = len(trail)
        if n < 2:
            return
        for i in range(0, n):
            alpha = int(30 + 180 * (i / n)) if active else 30
            c = QColor(color.red(), color.green(), color.blue(), alpha)
            w = 1.0 + 2.0 * (i / n) if active else 1.0
            p.setPen(QPen(c, w))
            x1, y1 = self.world_to_screen(*trail[i - 1])
            x2, y2 = self.world_to_screen(*trail[i])
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

    def _paint_vehicle(self, p: QPainter, v: VehicleState, active: bool):
        color = vehicle_color(v.vehicle_id)
        sx, sy = self.world_to_screen(v.position_x, v.position_y)
        R = 14

        # ── Ghost marker for lost vehicles ──
        if not active:
            ghost = QColor(color.red(), color.green(), color.blue(), 60)
            p.setPen(QPen(ghost, 1.5, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(sx, sy), R, R)
            if self.show_ids:
                p.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 80)))
                p.setFont(QFont("Consolas", 9))
                p.drawText(int(sx + R + 3), int(sy + 4), f"V{v.vehicle_id}")
            return

        # ── Glow ──
        glow = QRadialGradient(sx, sy, R * 2.5)
        glow.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 50))
        glow.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(QPointF(sx, sy), R * 2.5, R * 2.5)

        # ── Filled circle ──
        p.setPen(QPen(color, 2))
        p.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 160)))
        p.drawEllipse(QPointF(sx, sy), R, R)

        # ── Centre dot ──
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 255, 255, 200)))
        p.drawEllipse(QPointF(sx, sy), 3, 3)

        # ── Orientation arrow ──
        if self.show_orientation:
            arrow_len = 34
            dx = arrow_len * math.cos(v.yaw)
            dy = -arrow_len * math.sin(v.yaw)       # screen-Y is flipped
            tip_x, tip_y = sx + dx, sy + dy

            p.setPen(QPen(QColor(255, 255, 80), 2.5))
            p.drawLine(int(sx), int(sy), int(tip_x), int(tip_y))

            angle = math.atan2(dy, dx)
            hl = 9
            for sign in (1, -1):
                a = angle + math.pi * 0.82 * sign
                hx = tip_x + hl * math.cos(a)
                hy = tip_y + hl * math.sin(a)
                p.drawLine(int(tip_x), int(tip_y), int(hx), int(hy))

        # ── ID & position label ──
        if self.show_ids:
            p.setPen(QPen(color))
            p.setFont(QFont("Consolas", 11, QFont.Bold))
            p.drawText(int(sx + R + 5), int(sy - 4), f"V{v.vehicle_id}")
            p.setFont(QFont("Consolas", 8))
            p.setPen(QPen(QColor(180, 180, 200)))
            p.drawText(
                int(sx + R + 5),
                int(sy + 10),
                f"({v.position_x:.2f}, {v.position_y:.2f})",
            )

    def _paint_hud(self, p: QPainter):
        p.setPen(QPen(QColor(180, 180, 200)))
        p.setFont(QFont("Consolas", 9))
        now = time.time()
        active = sum(
            1
            for v in self.vehicles.values()
            if now - v.last_seen < self.vehicle_timeout
        )
        lines = [
            f"Scale : {self.scale:.0f} px/m",
            f"Centre: ({self.offset_x:.2f}, {self.offset_y:.2f}) m",
            f"Vehicles: {active} active / {len(self.vehicles)} total",
        ]
        y = 18
        for line in lines:
            p.drawText(8, y, line)
            y += 15

    # ── Mouse interaction ──────────────────────────────────────────

    def wheelEvent(self, event):
        pos = event.pos()
        wx, wy = self.screen_to_world(pos.x(), pos.y())
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale = max(5, min(12000, self.scale * factor))
        nwx, nwy = self.screen_to_world(pos.x(), pos.y())
        self.offset_x -= nwx - wx
        self.offset_y -= nwy - wy
        self.update()

    def mousePressEvent(self, event):
        if event.button() in (Qt.LeftButton, Qt.MiddleButton):
            self._dragging = True
            self._last_mouse = event.pos()

    def mouseMoveEvent(self, event):
        if self._dragging and self._last_mouse is not None:
            dx = event.pos().x() - self._last_mouse.x()
            dy = event.pos().y() - self._last_mouse.y()
            self.offset_x -= dx / self.scale
            self.offset_y += dy / self.scale
            self._last_mouse = event.pos()
            self.update()

    def mouseReleaseEvent(self, _event):
        self._dragging = False
        self._last_mouse = None

    def mouseDoubleClickEvent(self, event):
        wx, wy = self.screen_to_world(event.pos().x(), event.pos().y())
        self.offset_x = wx
        self.offset_y = wy
        self.update()