"""Top-level window: assembles the map canvas, table, and control panel."""

import time
from collections import deque

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .data_model import VehicleState
from .map_canvas import MapCanvas
from .ros_bridge import ROSBridge
from .vehicle_table import VehicleTable


class MainWindow(QMainWindow):

    def __init__(self, bridge: ROSBridge, parent=None):
        super().__init__(parent)
        self._bridge = bridge
        self.setWindowTitle("IPS — Vehicle Observation Visualizer")
        self.resize(1400, 850)

        self._apply_style()
        self._build_ui()

        # 20 Hz GUI refresh
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    # ── Theme ──────────────────────────────────────────────────────

    @staticmethod
    def _apply_style():
        QApplication.instance().setStyleSheet("""
            QMainWindow, QWidget#central { background-color: #14162a; }
            QGroupBox {
                color: #9898c0;
                border: 1px solid #2e3048;
                border-radius: 5px;
                margin-top: 10px;
                padding: 14px 8px 8px 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QLabel { color: #b8b8d0; font-size: 12px; }
            QPushButton {
                background-color: #262848;
                color: #d0d0e8;
                border: 1px solid #3e4068;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover  { background-color: #32325a; }
            QPushButton:pressed { background-color: #3e4068; }
            QCheckBox { color: #b8b8d0; spacing: 6px; font-size: 12px; }
            QCheckBox::indicator { width: 15px; height: 15px; }
            QSpinBox, QDoubleSpinBox {
                background-color: #1e2038;
                color: #d0d0e8;
                border: 1px solid #3e4068;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 12px;
            }
        """)

    # ── Layout ─────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # ── Left: map ──
        self.canvas = MapCanvas()

        # ── Right: controls + table ──
        right = QWidget()
        rcol = QVBoxLayout(right)
        rcol.setContentsMargins(0, 0, 0, 0)
        rcol.setSpacing(6)

        # --- View Controls ---
        vg = QGroupBox("View Controls")
        vl = QVBoxLayout(vg)

        btn_row = QHBoxLayout()
        self.btn_reset = QPushButton("Reset View")
        self.btn_fit = QPushButton("Fit Active")
        self.btn_clear = QPushButton("Clear Trails")
        btn_row.addWidget(self.btn_reset)
        btn_row.addWidget(self.btn_fit)
        btn_row.addWidget(self.btn_clear)
        vl.addLayout(btn_row)

        self.btn_reset.clicked.connect(self.canvas.reset_view)
        self.btn_fit.clicked.connect(self.canvas.fit_active_vehicles)
        self.btn_clear.clicked.connect(self._clear_trails)

        self.chk_trails = QCheckBox("Trails")
        self.chk_trails.setChecked(True)
        self.chk_ids = QCheckBox("IDs & Coords")
        self.chk_ids.setChecked(True)
        self.chk_orient = QCheckBox("Orientation")
        self.chk_orient.setChecked(True)
        self.chk_grid = QCheckBox("Grid")
        self.chk_grid.setChecked(True)

        self.chk_trails.toggled.connect(
            lambda v: setattr(self.canvas, "show_trails", v)
        )
        self.chk_ids.toggled.connect(
            lambda v: setattr(self.canvas, "show_ids", v)
        )
        self.chk_orient.toggled.connect(
            lambda v: setattr(self.canvas, "show_orientation", v)
        )
        self.chk_grid.toggled.connect(
            lambda v: setattr(self.canvas, "show_grid", v)
        )

        for cb in (self.chk_trails, self.chk_ids, self.chk_orient, self.chk_grid):
            vl.addWidget(cb)
        rcol.addWidget(vg)

        # --- Settings ---
        sg = QGroupBox("Settings")
        sl = QFormLayout(sg)

        self.spin_timeout = QDoubleSpinBox()
        self.spin_timeout.setRange(0.3, 60.0)
        self.spin_timeout.setValue(2.0)
        self.spin_timeout.setSingleStep(0.5)
        self.spin_timeout.setSuffix(" s")
        self.spin_timeout.valueChanged.connect(
            lambda v: setattr(self.canvas, "vehicle_timeout", v)
        )
        sl.addRow("Timeout:", self.spin_timeout)

        self.spin_trail = QSpinBox()
        self.spin_trail.setRange(10, 5000)
        self.spin_trail.setValue(300)
        self.spin_trail.setSingleStep(50)
        self.spin_trail.valueChanged.connect(self._set_trail_len)
        sl.addRow("Trail pts:", self.spin_trail)
        rcol.addWidget(sg)

        # --- Vehicle table ---
        tg = QGroupBox("Vehicle Details")
        tl = QVBoxLayout(tg)
        self.table = VehicleTable()
        tl.addWidget(self.table)
        rcol.addWidget(tg, stretch=1)

        # --- Status bar ---
        self.lbl_status = QLabel("Waiting for observations…")
        self.lbl_status.setStyleSheet(
            "color:#6868a0; font-size:11px; padding:4px;"
        )
        rcol.addWidget(self.lbl_status)

        # ── Splitter ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([1050, 350])
        splitter.setHandleWidth(4)
        root.addWidget(splitter)

    # ── Helpers ────────────────────────────────────────────────────

    def _clear_trails(self):
        vehicles = self._bridge.snapshot()
        for v in vehicles.values():
            v.trail.clear()

    def _set_trail_len(self, maxlen: int):
        vehicles = self._bridge.snapshot()
        for v in vehicles.values():
            v.trail = deque(v.trail, maxlen=maxlen)

    # ── Refresh tick (20 Hz) ───────────────────────────────────────

    def _tick(self):
        vehicles = self._bridge.snapshot()
        self.canvas.update_vehicles(vehicles)
        self.table.refresh(vehicles, self.canvas.vehicle_timeout)

        now = time.time()
        active = sum(
            1
            for v in vehicles.values()
            if now - v.last_seen < self.canvas.vehicle_timeout
        )
        total = len(vehicles)
        self.lbl_status.setText(
            f"Tracked: {total}  |  Active: {active}  |  Refresh: 20 Hz"
        )