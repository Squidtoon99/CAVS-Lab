"""QTableWidget that shows per-vehicle details (x, y, yaw, status)."""

import math
import time
from typing import Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

from .data_model import VehicleState


class VehicleTable(QTableWidget):
    """Tabular display of vehicle state refreshed by the main window."""

    COLUMNS = ["ID", "Status", "X (m)", "Y (m)", "Yaw (°)", "Msgs", "Age (s)"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1a1c2e;
                alternate-background-color: #1f2136;
                color: #c8c8dc;
                gridline-color: #2e3048;
                font-family: Consolas;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #262840;
                color: #9898b8;
                padding: 4px;
                border: 1px solid #2e3048;
                font-weight: bold;
            }
        """)

    def refresh(self, vehicles: Dict[int, VehicleState], timeout: float):
        now = time.time()
        rows = sorted(
            vehicles.values(),
            key=lambda v: (now - v.last_seen > timeout, v.vehicle_id),
        )
        self.setRowCount(len(rows))
        for r, v in enumerate(rows):
            age = now - v.last_seen
            active = age < timeout
            vals = [
                str(v.vehicle_id),
                "● Active" if active else "○ Lost",
                f"{v.position_x:.4f}",
                f"{v.position_y:.4f}",
                f"{math.degrees(v.yaw):.1f}",
                str(v.msg_count),
                f"{age:.1f}",
            ]
            for c, txt in enumerate(vals):
                item = QTableWidgetItem(txt)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(
                    QColor(80, 240, 120) if active else QColor(240, 80, 80)
                )
                self.setItem(r, c, item)