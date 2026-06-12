"""Exponential moving average - landmark titrog'ini (jitter) silliqlash."""


class EMA:
    def __init__(self, alpha: float):
        self.alpha = alpha
        self._value: float | None = None

    def update(self, x: float) -> float:
        if self._value is None:
            self._value = x
        else:
            self._value = self.alpha * x + (1 - self.alpha) * self._value
        return self._value

    def reset(self) -> None:
        self._value = None
