import json
from pathlib import Path

_PROTECTED_FILE = Path(__file__).parent.parent / "protected.json"

_cache: dict[str, frozenset[str]] | None = None
_cache_mtime: float | None = None


def get_protected(manager: str) -> frozenset[str]:
    global _cache, _cache_mtime
    try:
        mtime = _PROTECTED_FILE.stat().st_mtime
    except OSError:
        return frozenset()
    if _cache is None or mtime != _cache_mtime:
        try:
            data = json.loads(_PROTECTED_FILE.read_text(encoding="utf-8"))
            _cache = {mgr: frozenset(v) for mgr, v in data.items()}
            _cache_mtime = mtime
        except Exception:
            _cache = {}
            _cache_mtime = mtime
    return _cache.get(manager, frozenset())


def is_protected(manager: str, name: str) -> bool:
    return name.lower() in get_protected(manager)
