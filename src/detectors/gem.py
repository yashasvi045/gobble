import re
from .base import BaseDetector, PackageEntry
from .process import run_cmd
from src.protected import is_protected


class GemDetector(BaseDetector):
    name = "gem"

    def detect(self) -> list[PackageEntry]:
        if not self.is_available():
            return []
        try:
            result = run_cmd(
                ["gem", "list", "--no-verbose"],
                capture_output=True, text=True, timeout=15
            )
            packages = []
            for line in result.stdout.splitlines():
                match = re.match(r"^(\S+)\s+\(([\d., ]+)\)", line)
                if match:
                    version = match.group(2).split(",")[0].strip()
                    name = match.group(1)
                    if not is_protected("gem", name):
                        packages.append(PackageEntry(
                            manager="gem",
                            name=name,
                            version=version
                        ))
            return packages
        except Exception:
            return []

    def uninstall(self, package: str) -> tuple[bool, str]:
        try:
            result = run_cmd(
                ["gem", "uninstall", "-x", package],
                capture_output=True, text=True, timeout=60
            )
            success = result.returncode == 0
            return success, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
