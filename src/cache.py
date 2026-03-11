import sys
import json
from pathlib import Path
from src.detectors import PackageEntry

_CACHE_FILE = (
    Path.home() / ".gobble_cache.json"
    if getattr(sys, "frozen", False)
    else Path(__file__).parent.parent / ".gobble_cache.json"
)


def save_cache(packages: list[PackageEntry]) -> None:
    data = [{"manager": p.manager, "name": p.name, "version": p.version} for p in packages]
    try:
        _CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass


def load_cache() -> list[PackageEntry]:
    if not _CACHE_FILE.exists():
        return []
    try:
        data = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        return [PackageEntry(manager=d["manager"], name=d["name"], version=d["version"]) for d in data]
    except Exception:
        return []
