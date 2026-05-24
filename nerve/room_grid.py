"""JEPAGrid — numpy fallback for Cocapn Fleet."""

from __future__ import annotations
__all__ = ["JEPAGrid", "Fingerprint"]

import math
import numpy as np
from dataclasses import dataclass


def make_weights(n: int, d: int = 64, h: int = 32, l: int = 16, seed: int = 42):
    rng = np.random.RandomState(seed)
    return {
        "w1": rng.randn(n, d, h).astype(np.float32) * 0.01,
        "b1": np.zeros((1, n, h), dtype=np.float32),
        "w2": rng.randn(n, h, l).astype(np.float32) * 0.01,
        "b2": np.zeros((1, n, l), dtype=np.float32),
        "w3": rng.randn(n, l, l).astype(np.float32) * 0.01,
        "b3": np.zeros((1, n, l), dtype=np.float32),
    }


@dataclass
class Fingerprint:
    i: int
    sine: np.ndarray
    noise: np.ndarray
    step: np.ndarray
    activity: int

    def diff(self, other):
        n = lambda a, b: np.linalg.norm(a - b)
        return float(n(self.sine, other.sine) + n(self.noise, other.noise) + n(self.step, other.step))

    def __repr__(self):
        return f"Fingerprint(room={self.i}, activity={self.activity})"


class JEPAGrid:
    """N rooms × JEPA.  Numpy fallback."""

    def __init__(self, n=250, d=64, h=32, l=16, chaos=0.3):
        self.n = n
        self.w = make_weights(n, d, h, l)
        self.activity = np.zeros(n, dtype=np.int32)
        self.chaos = np.full(n, chaos, dtype=np.float32)
        self.history = {}
        self.ticks = 0
        self.l = l
        t = np.linspace(0, 2 * math.pi, d)
        self._ref = {
            "sine": np.sin(t).astype(np.float32),
            "noise": np.random.randn(d).astype(np.float32),
            "step": np.concatenate([np.zeros(d // 2), np.ones(d // 2)]).astype(np.float32),
        }
        self._flux_checker = None  # attached via attach_flux_checker()

    def tick(self, x):
        """Run one grid tick.  Returns basic stats."""
        self.ticks += 1
        # Minimal tick: just increment activity for some rooms
        fired = []
        for i in range(self.n):
            if np.random.random() < self.chaos[i]:
                self.activity[i] += 1
                fired.append(i)
        return {"fired": len(fired), "ids": fired[:10], "tick": self.ticks}

    def top(self, k=10):
        idx = np.argsort(self.activity)[::-1][:k]
        return [(int(i), int(self.activity[i])) for i in idx]

    def cold(self, thresh=1):
        return [int(i) for i in range(self.n) if self.activity[i] < thresh]

    def rebirth(self, i):
        rng = np.random.RandomState(i + 9999)
        for k, shp in [("w1", (64, 32)), ("w2", (32, 16)), ("w3", (16, 16))]:
            self.w[k][i] = rng.randn(*shp).astype(np.float32) * 0.01
        self.activity[i] = 0
        self.chaos[i] = 0.3
        self.history[i] = []

    def breed(self, src, dst):
        """Rebirth dst with weights cloned from src + light mutation."""
        for k in ("w1", "w2", "w3"):
            self.w[k][dst] = self.w[k][src].copy()
        rng = np.random.RandomState(dst + 8888)
        for k in ("w1", "w2", "w3"):
            self.w[k][dst] += rng.randn(*self.w[k][dst].shape).astype(np.float32) * 0.005
        self.activity[dst] = 0
        self.chaos[dst] = 0.3
        self.history[dst] = []

    def attach_flux_checker(self, checker):
        """Attach a FLUX constraint checker (Path A integration hook)."""
        self._flux_checker = checker

    @property
    def stats(self):
        a = int((self.activity > 0).sum())
        return {"rooms": self.n, "ticks": self.ticks, "active": a, "cold": self.n - a, "pct": f"{a / self.n * 100:.1f}%"}

    def __repr__(self):
        return f"JEPAGrid(n={self.n}, ticks={self.ticks}, active={int((self.activity > 0).sum())}, numpy)"
