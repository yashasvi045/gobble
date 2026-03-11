from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PackageEntry:
    manager: str
    name: str
    version: str


class BaseDetector(ABC):
    name: str = ""

    @abstractmethod
    def detect(self) -> list[PackageEntry]:
        ...

    @abstractmethod
    def uninstall(self, package: str) -> tuple[bool, str]:
        ...

    def is_available(self) -> bool:
        import shutil
        return shutil.which(self.name) is not None
