import json
from .base import BaseDetector, PackageEntry
from .process import run_cmd
from src.protected import is_protected


class NpmDetector(BaseDetector):
    name = "npm"

    def detect(self) -> list[PackageEntry]:
        if not self.is_available():
            return []
        try:
            result = run_cmd(
                ["npm", "list", "-g", "--depth=0", "--json"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            deps = data.get("dependencies", {})
            return [
                PackageEntry(manager="npm", name=name, version=info.get("version", "unknown"))
                for name, info in deps.items()
                if not is_protected("npm", name)
            ]
        except Exception:
            return []

    def uninstall(self, package: str) -> tuple[bool, str]:
        try:
            result = run_cmd(
                ["npm", "uninstall", "-g", package],
                capture_output=True, text=True, timeout=60
            )
            success = result.returncode == 0
            return success, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
