import sys
import ctypes
from pathlib import Path

FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"


def load_fonts() -> None:
    font_files = list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf"))
    if not font_files:
        return

    if sys.platform == "win32":
        _load_windows(font_files)
    elif sys.platform == "darwin":
        _load_macos(font_files)
    else:
        _load_linux(font_files)


def _load_windows(font_files: list[Path]) -> None:
    FR_PRIVATE = 0x10
    for path in font_files:
        ctypes.windll.gdi32.AddFontResourceExW(str(path), FR_PRIVATE, 0)


def _load_macos(font_files: list[Path]) -> None:
    import ctypes.util
    ct = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreText"))
    cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))

    cf.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
    cf.CFURLCreateFromFileSystemRepresentation.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_bool,
    ]
    ct.CTFontManagerRegisterFontsForURL.restype = ctypes.c_bool
    ct.CTFontManagerRegisterFontsForURL.argtypes = [
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p,
    ]

    kCTFontManagerScopeProcess = 1
    for path in font_files:
        path_bytes = str(path).encode("utf-8")
        url = cf.CFURLCreateFromFileSystemRepresentation(None, path_bytes, len(path_bytes), False)
        ct.CTFontManagerRegisterFontsForURL(url, kCTFontManagerScopeProcess, None)


def _load_linux(font_files: list[Path]) -> None:
    import shutil
    import subprocess

    font_dir = Path.home() / ".local" / "share" / "fonts" / "gobble"
    font_dir.mkdir(parents=True, exist_ok=True)
    for path in font_files:
        dest = font_dir / path.name
        if not dest.exists():
            shutil.copy(path, dest)
    subprocess.run(["fc-cache", "-f", str(font_dir)], capture_output=True)
