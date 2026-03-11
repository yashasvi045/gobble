import json
from .base import BaseDetector, PackageEntry
from .process import run_cmd
from src.protected import is_protected


class PipDetector(BaseDetector):
    name = "pip"

    def detect(self) -> list[PackageEntry]:
        if not self.is_available():
            return []
        try:
            result = run_cmd(
                ["pip", "list", "--format=json"],
                capture_output=True, text=True, timeout=15
            )
            packages = json.loads(result.stdout)
            return [
                PackageEntry(manager="pip", name=pkg["name"], version=pkg["version"])
                for pkg in packages
                if not is_protected("pip", pkg["name"])
            ]
        except Exception:
            return []

    def uninstall(self, package: str) -> tuple[bool, str]:
        try:
            result = run_cmd(
                ["pip", "uninstall", "-y", package],
                capture_output=True, text=True, timeout=60
            )
            success = result.returncode == 0
            return success, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
