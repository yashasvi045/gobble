import re
from .base import BaseDetector, PackageEntry
from .process import run_cmd


class CargoDetector(BaseDetector):
    name = "cargo"

    def detect(self) -> list[PackageEntry]:
        if not self.is_available():
            return []
        try:
            result = run_cmd(
                ["cargo", "install", "--list"],
                capture_output=True, text=True, timeout=15
            )
            packages = []
            for line in result.stdout.splitlines():
                match = re.match(r"^(\S+)\s+v([\d.]+\S*):", line)
                if match:
                    packages.append(PackageEntry(
                        manager="cargo",
                        name=match.group(1),
                        version=match.group(2)
                    ))
            return packages
        except Exception:
            return []

    def uninstall(self, package: str) -> tuple[bool, str]:
        try:
            result = run_cmd(
                ["cargo", "uninstall", package],
                capture_output=True, text=True, timeout=120
            )
            success = result.returncode == 0
            return success, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
