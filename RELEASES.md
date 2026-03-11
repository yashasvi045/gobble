# Releases

## v1.0.0 — 2026-03-11

Initial release.

### Features
- Scan globally installed packages across pip, npm, cargo, and gem
- One-click uninstall with confirmation dialog
- Persistent scan cache (`.gobble_cache.json`) for instant re-display between sessions
- Light / dark theme toggle (initially follows system default theme via `darkdetect`)
- Package name validation before uninstall to prevent shell injection
