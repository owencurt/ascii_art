from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .config import ControlConfig


@dataclass
class DetailState:
    normalized_detail: float


class DetailController:
    def __init__(self, config: ControlConfig) -> None:
        self.config = config
        self._smoothed = 0.35

    def update(self, raise_amount: Optional[float]) -> DetailState:
        if raise_amount is None:
            self._smoothed *= self.config.fallback_decay
            self._smoothed = self._clamp(self._smoothed, 0.0, 1.0)
            return DetailState(normalized_detail=self._smoothed)

        normalized = self._normalize_raise(raise_amount)
        normalized = normalized**self.config.detail_gamma
        self._smoothed = (1.0 - self.config.smoothing_alpha) * self._smoothed + self.config.smoothing_alpha * normalized
        self._smoothed = self._clamp(self._smoothed, 0.0, 1.0)
        return DetailState(normalized_detail=self._smoothed)

    def _normalize_raise(self, raise_amount: float) -> float:
        shifted = self._clamp(raise_amount, self.config.min_raise, self.config.max_raise)
        unit = (shifted - self.config.min_raise) / (self.config.max_raise - self.config.min_raise)

        if unit < self.config.deadband:
            return 0.0
        if unit > 1.0 - self.config.deadband:
            return 1.0
        return (unit - self.config.deadband) / (1.0 - 2.0 * self.config.deadband)

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))
