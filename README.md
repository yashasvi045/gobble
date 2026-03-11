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
├── main.py
├── requirements.txt
├── gobble.spec
├── protected.json
├── assets/
│   ├── gobbleicon.ico
│   ├── gobbleicon.png
│   ├── gobble_theme.json
│   └── fonts/
└── src/
    ├── app.py
    ├── uninstaller.py
    ├── cache.py
    ├── protected.py
    ├── font_loader.py
    ├── version.py
    └── detectors/
        ├── base.py
        ├── process.py
        ├── npm.py
        ├── pip.py
        ├── cargo.py
        └── gem.py
```

---

## License

MIT
