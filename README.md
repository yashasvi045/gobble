# Gobble

> A cross-platform GUI tool to detect and remove globally installed packages, because all dependencies should live in project-scoped environments.

---

## Why?

Modern development best practices keep dependencies project-scoped:

- Node.js → `node_modules/` with `package.json`
- Python → `venv/`, `poetry`, or `pipenv`
- Rust → per-project `Cargo.toml`

Over time, developers accumulate a graveyard of globally installed packages that cause version conflicts, break reproducibility, and create _"works on my machine"_ problems.

**Gobble scans your machine, shows you what's globally installed, and lets you remove it — with a single click.**

---

## Supported Package Managers

| Manager | Lists via | Uninstalls via |
|---|---|---|
| **npm** | `npm list -g --depth=0` | `npm uninstall -g <pkg>` |
| **pip** | `pip list` | `pip uninstall -y <pkg>` |
| **cargo** | `cargo install --list` | `cargo uninstall <pkg>` |
| **gem** | `gem list` | `gem uninstall <pkg>` |
| **conda** | `conda list -n base` | `conda remove -n base <pkg>` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| GUI | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Packaging | [PyInstaller](https://pyinstaller.org/) |

---

## Platform Support

| Platform | Status |
|---|---|
| Windows | ✅ Supported |
| macOS | ✅ Supported |
| Linux | ✅ Supported |

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- `pip`

### Run from source

```bash
git clone https://github.com/yourname/gobble.git
cd gobble
pip install -r requirements.txt
python main.py
```

### Build a standalone executable

```bash
pip install pyinstaller
pyinstaller gobble.spec
```

The output will be in `dist/gobble/`. Distribute just that folder or use `--onefile` for a single `.exe`/binary.

---

## Usage

1. Launch **Gobble**
2. Click **Scan** to detect globally installed packages across all supported managers
3. Review the list — each package shows its manager, name, and version
4. Check the packages you want to remove
5. Click **Uninstall Selected**
6. Watch the output log for progress and confirmation

---

## Project Structure

```
gobble/
├── main.py                  # Entry point
├── requirements.txt         # Runtime dependencies
├── gobble.spec              # PyInstaller build config
├── assets/
│   └── icon.ico             # App icon
└── src/
    ├── app.py               # Main GUI window (CustomTkinter)
    ├── uninstaller.py       # Runs uninstall commands asynchronously
    └── detectors/
        ├── base.py          # Abstract base class for detectors
        ├── npm.py           # npm global package detector
        ├── pip.py           # pip global package detector
        ├── cargo.py         # cargo installed binaries detector
        └── gem.py           # Ruby gem detector
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/add-pnpm-detector`
3. Add your detector in `src/detectors/` following the pattern in `base.py`
4. Submit a pull request

### Adding a new package manager detector

Create a new file in `src/detectors/` that extends `BaseDetector`:

```python
from .base import BaseDetector, PackageEntry

class MyManagerDetector(BaseDetector):
    name = "mymanager"

    def detect(self) -> list[PackageEntry]:
        # run CLI, parse output, return list of PackageEntry
        ...

    def uninstall(self, package: str) -> tuple[bool, str]:
        # run uninstall command, return (success, output)
        ...
```

Then register it in `src/detectors/__init__.py`.

---

## License

MIT
