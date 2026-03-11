from .base import BaseDetector, PackageEntry
from .npm import NpmDetector
from .pip import PipDetector
from .cargo import CargoDetector
from .gem import GemDetector

ALL_DETECTORS: list[type[BaseDetector]] = [
    NpmDetector,
    PipDetector,
    CargoDetector,
    GemDetector,
]

__all__ = [
    "BaseDetector",
    "PackageEntry",
    "NpmDetector",
    "PipDetector",
    "CargoDetector",
    "GemDetector",
    "ALL_DETECTORS",
]
