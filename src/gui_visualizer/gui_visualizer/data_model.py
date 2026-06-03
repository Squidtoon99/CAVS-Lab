"""Single dataclass holding per-vehicle state for the GUI."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Tuple


@dataclass
class VehicleState:
    """Latest observation + trail history for one vehicle."""

    vehicle_id: int
    position_x: float = 0.0
    position_y: float = 0.0
    yaw: float = 0.0
    last_seen: float = 0.0
    msg_count: int = 0
    trail: Deque[Tuple[float, float]] = field(
        default_factory=lambda: deque(maxlen=300)
    )