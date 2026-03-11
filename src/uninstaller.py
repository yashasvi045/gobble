import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable
from src.detectors import ALL_DETECTORS, PackageEntry

_SAFE_PACKAGE_NAME = re.compile(r"^[A-Za-z0-9@/_\.\-+:]+$")


def scan_all(
    on_done: Callable[[list[PackageEntry]], None],
    on_error: Callable[[str, Exception], None] | None = None,
) -> None:
    def _run():
        results: list[PackageEntry] = []
        with ThreadPoolExecutor(max_workers=len(ALL_DETECTORS)) as pool:
            futures = {pool.submit(cls().detect): cls for cls in ALL_DETECTORS}
            for future in as_completed(futures):
                cls = futures[future]
                try:
                    results.extend(future.result())
                except Exception as exc:
                    if on_error:
                        on_error(cls.__name__, exc)
        on_done(results)

    threading.Thread(target=_run, daemon=True).start()


def uninstall_packages(
    packages: list[PackageEntry],
    on_progress: Callable[[str], None],
    on_done: Callable[[], None],
    on_package_done: Callable[[PackageEntry, bool], None] | None = None,
) -> None:
    def _run():
        detector_map = {cls.name: cls() for cls in ALL_DETECTORS}
        for pkg in packages:
            if not _SAFE_PACKAGE_NAME.match(pkg.name):
                on_progress(f"[SKIP] Rejected unsafe package name: {pkg.name}\n")
                if on_package_done:
                    on_package_done(pkg, False)
                continue
            detector = detector_map.get(pkg.manager)
            if detector is None:
                on_progress(f"[SKIP] No detector for manager: {pkg.manager}\n")
                if on_package_done:
                    on_package_done(pkg, False)
                continue
            on_progress(f"[{pkg.manager}] Uninstalling {pkg.name}...\n")
            success, output = detector.uninstall(pkg.name)
            status = "OK" if success else "FAILED"
            on_progress(f"[{status}] {pkg.name}\n{output}\n")
            if on_package_done:
                on_package_done(pkg, success)
        on_done()

    threading.Thread(target=_run, daemon=True).start()
