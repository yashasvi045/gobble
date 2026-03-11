import sys
import json
import customtkinter as ctk
from tkinter import filedialog, PhotoImage
from pathlib import Path
from src.detectors import PackageEntry
from src.uninstaller import scan_all, uninstall_packages
from src.font_loader import load_fonts
from src.cache import save_cache, load_cache
from src.version import __version__

_ASSETS = Path(__file__).parent.parent / "assets"


def _init_ctk() -> None:
    load_fonts()
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme(str(_ASSETS / "gobble_theme.json"))


_ctk_initialized = False

_FONT_FAMILY = "Inter"


def _font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=_FONT_FAMILY, size=size, weight=weight)


class GobbleApp(ctk.CTk):
    def __init__(self):
        global _ctk_initialized
        if not _ctk_initialized:
            _init_ctk()
            _ctk_initialized = True
        super().__init__()
        self.title(f"Gobble v{__version__}")
        self.geometry("900x620")
        self.resizable(False, False)
        self._set_icon()

        self._packages: list[PackageEntry] = []
        self._checkboxes: list[tuple[ctk.CTkCheckBox, PackageEntry]] = []
        self._row_status_labels: dict[int, ctk.CTkLabel] = {}
        self._is_dark = ctk.get_appearance_mode().lower() == "dark"
        self._select_all_state = False

        self._build_ui()

        cached = load_cache()
        if cached:
            self._packages = cached
            managers = ["All"] + sorted({p.manager for p in cached})
            self._manager_menu.configure(values=managers)
            self._populate_list(cached)
            self._status_label.configure(text=f"Showing {len(cached)} cached package(s) from last scan.")

    def _set_icon(self):
        ico = _ASSETS / "gobbleicon.ico"
        png = _ASSETS / "gobbleicon.png"
        if png.exists():
            self._icon_ref = PhotoImage(file=str(png))
            self.iconphoto(True, self._icon_ref)
        if ico.exists() and sys.platform == "win32":
            self.iconbitmap(str(ico))

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(self, height=50)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        self._scan_btn = ctk.CTkButton(top, text="Scan", width=120, font=_font(13, "bold"), command=self._on_scan)
        self._scan_btn.grid(row=0, column=0, padx=10, pady=8)

        self._export_btn = ctk.CTkButton(top, text="Export", width=90, font=_font(13), command=self._on_export, state="disabled")
        self._export_btn.grid(row=0, column=1, padx=(0, 6), pady=8)

        self._status_label = ctk.CTkLabel(top, text="Scan to detect globally installed packages.", font=_font(13))
        self._status_label.grid(row=0, column=2, sticky="w", padx=5)

        self._uninstall_btn = ctk.CTkButton(
            top, text="Uninstall Selected", width=160,
            font=_font(13, "bold"),
            fg_color="red", hover_color="#cc0000",
            text_color="white", text_color_disabled="white",
            command=self._on_uninstall, state="disabled"
        )
        self._uninstall_btn.grid(row=0, column=3, padx=10, pady=8)

        self._theme_btn = ctk.CTkButton(
            top, text=self._theme_icon(), width=40,
            font=_font(16),
            command=self._toggle_theme
        )
        self._theme_btn.grid(row=0, column=4, padx=(4, 6), pady=8)

        self._dry_run_var = ctk.BooleanVar(value=False)
        dry_run_cb = ctk.CTkCheckBox(
            top, text="Dry Run", font=_font(12),
            variable=self._dry_run_var,
            command=self._on_dry_run_toggle,
        )
        dry_run_cb.grid(row=0, column=5, padx=(0, 10), pady=8)
        top.grid_columnconfigure(2, weight=1)

        filter_bar = ctk.CTkFrame(self, height=36, fg_color="transparent")
        filter_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(6, 0))
        filter_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(filter_bar, text="Filter:", font=_font(13)).grid(row=0, column=0, padx=(0, 6))

        self._manager_var = ctk.StringVar(value="All")
        self._manager_menu = ctk.CTkOptionMenu(
            filter_bar, variable=self._manager_var,
            values=["All"], font=_font(13), width=120,
            command=lambda _: self._apply_filters()
        )
        self._manager_menu.grid(row=0, column=1, sticky="w", padx=(0, 10))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._apply_filters())
        search_entry = ctk.CTkEntry(filter_bar, textvariable=self._search_var, placeholder_text="Search packages…", font=_font(13))
        search_entry.grid(row=0, column=2, sticky="ew", padx=(0, 4))
        filter_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            filter_bar, text="🔍", width=36, height=28,
            font=_font(14), command=self._apply_filters,
            fg_color="transparent", hover_color=("gray80", "gray30"),
            border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray20", "gray90"),
        ).grid(row=0, column=3, padx=(0, 10))

        self._list_frame = ctk.CTkScrollableFrame(self, label_text="Global Packages", label_font=_font(13, "bold"))
        self._list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self._list_frame.grid_columnconfigure(0, minsize=30)
        self._list_frame.grid_columnconfigure(1, minsize=80)
        self._list_frame.grid_columnconfigure(2, weight=1)
        self._list_frame.grid_columnconfigure(3, minsize=100)
        self._list_frame.grid_columnconfigure(4, minsize=60)

        self._log = ctk.CTkTextbox(self, height=150, state="disabled", font=_font(12), wrap="word")
        self._log.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        self._log._y_scrollbar.grid_remove()
        self._log_append(
            "Why Gobble?\n\n"
            "Modern development best practices keep dependencies project-scoped — Node.js via node_modules/, "
            "Python via venv/ or poetry, Rust via Cargo.toml. Over time, developers accumulate a graveyard of "
            "globally installed packages that cause version conflicts, break reproducibility, and create "
            "\"works on my machine\" problems.\n\n"
            "Gobble scans your machine, shows you what's globally installed, and lets you remove it — with a single click."
        )

    def _on_scan(self):
        self._scan_btn.configure(state="disabled")
        self._uninstall_btn.configure(state="disabled")
        self._status_label.configure(text="Scanning...")
        self._clear_list()
        scan_all(self._on_scan_done, on_error=self._on_scan_error)

    def _on_scan_done(self, packages: list[PackageEntry]):
        save_cache(packages)
        managers = ["All"] + sorted({p.manager for p in packages})

        def _apply():
            self._packages = packages
            self._scan_btn.configure(state="normal")
            self._export_btn.configure(state="normal" if packages else "disabled")
            self._status_label.configure(text=f"Found {len(packages)} global package(s).")
            self._manager_menu.configure(values=managers)
            self._manager_var.set("All")
            self._populate_list(packages)

        self.after(0, _apply)

    def _on_scan_error(self, detector_name: str, exc: Exception):
        self.after(0, lambda: self._log_append(f"[ERROR] {detector_name} failed: {exc}\n"))

    def _on_uninstall(self):
        selected = [pkg for cb, pkg in self._checkboxes if cb.get()]
        if not selected:
            return
        if not self._confirm_uninstall(selected):
            return
        self._uninstall_btn.configure(state="disabled")
        self._scan_btn.configure(state="disabled")

        if self._dry_run_var.get():
            self._log_append(f"[DRY RUN] Would uninstall {len(selected)} package(s):\n")
            for pkg in selected:
                self._log_append(f"  [{pkg.manager}] {pkg.name} {pkg.version}\n")
            self._log_append("[DRY RUN] No packages were removed.\n")
            self._scan_btn.configure(state="normal")
            self._uninstall_btn.configure(state="normal")
            return

        self._log_append(f"Uninstalling {len(selected)} package(s)...\n")

        pkg_to_row = {pkg: i + 1 for i, (_, pkg) in enumerate(self._checkboxes)}

        def _on_pkg_done(pkg: PackageEntry, success: bool):
            row = pkg_to_row.get(pkg)
            if row and row in self._row_status_labels:
                text = "✓" if success else "✗"
                color = "#22c55e" if success else "#ef4444"
                self.after(0, lambda t=text, c=color, r=row: (
                    self._row_status_labels[r].configure(text=t, text_color=c)
                ))

        uninstall_packages(
            selected,
            on_progress=lambda msg: self.after(0, lambda m=msg: self._log_append(m)),
            on_done=lambda: self.after(0, self._on_uninstall_done),
            on_package_done=_on_pkg_done,
        )

    def _confirm_uninstall(self, selected: list[PackageEntry]) -> bool:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Uninstall")
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self)

        names = ", ".join(p.name for p in selected[:5])
        if len(selected) > 5:
            names += f" and {len(selected) - 5} more"

        ctk.CTkLabel(
            dialog,
            text=f"Uninstall {len(selected)} package(s)?",
            font=_font(15, "bold")
        ).pack(pady=(24, 6))
        ctk.CTkLabel(
            dialog,
            text=names,
            font=_font(12),
            wraplength=380
        ).pack(pady=(0, 20))

        confirmed = ctk.BooleanVar(value=False)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()
        ctk.CTkButton(
            btn_frame, text="Cancel", width=120, font=_font(13),
            command=dialog.destroy
        ).grid(row=0, column=0, padx=10)
        ctk.CTkButton(
            btn_frame, text="Uninstall", width=120, font=_font(13, "bold"),
            fg_color="red", hover_color="#cc0000", text_color="white",
            command=lambda: [confirmed.set(True), dialog.destroy()]
        ).grid(row=0, column=1, padx=10)

        self.wait_window(dialog)
        return confirmed.get()

    def _on_uninstall_done(self):
        self._log_append("Done. Rescanning…\n")
        self._status_label.configure(text="Rescanning…")
        self._clear_list()
        scan_all(self._on_scan_done, on_error=self._on_scan_error)

    def _on_dry_run_toggle(self):
        if self._dry_run_var.get():
            self._uninstall_btn.configure(text="Simulate Uninstall")
            self._log_append("Dry Run enabled — no packages will be removed.\n")
        else:
            self._uninstall_btn.configure(text="Uninstall Selected")
            self._log_append("Dry Run disabled — uninstalls are live.\n")

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        new_mode = "Dark" if self._is_dark else "Light"
        self._theme_btn.configure(state="disabled")
        self._fade_and_switch(new_mode, step=0)

    def _fade_and_switch(self, new_mode: str, step: int):
        alphas = [1.0, 0.75, 0.5, 0.5, 0.75, 1.0]
        switch_at = 3

        if step == switch_at:
            ctk.set_appearance_mode(new_mode)
            self._theme_btn.configure(text=self._theme_icon())

        self.attributes("-alpha", alphas[step])

        if step < len(alphas) - 1:
            self.after(30, lambda: self._fade_and_switch(new_mode, step + 1))
        else:
            self.attributes("-alpha", 1.0)
            self._theme_btn.configure(state="normal")

    def _theme_icon(self) -> str:
        return "☀" if self._is_dark else "☾"

    def _on_export(self):
        if not self._packages:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Text", "*.txt"), ("All files", "*.*")],
            initialfile="gobble-packages",
        )
        if not path:
            return
        if path.endswith(".txt"):
            content = "\n".join(f"{p.manager}\t{p.name}\t{p.version}" for p in self._packages)
        else:
            content = json.dumps(
                [{"manager": p.manager, "name": p.name, "version": p.version} for p in self._packages],
                indent=2
            )
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._log_append(f"Exported {len(self._packages)} package(s) to {path}\n")
        except OSError as e:
            self._log_append(f"Export failed: {e}\n")

    def _on_select_all_toggle(self):
        check = self._select_all_var.get()
        for cb, _ in self._checkboxes:
            cb.select() if check else cb.deselect()

    def _apply_filters(self):
        if not self._packages:
            return
        manager = self._manager_var.get()
        query = self._search_var.get().lower()
        filtered = [
            p for p in self._packages
            if (manager == "All" or p.manager == manager)
            and (query == "" or query in p.name.lower())
        ]
        self._populate_list(filtered)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _clear_list(self):
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        self._checkboxes.clear()

    def _populate_list(self, packages: list[PackageEntry]):
        self._clear_list()
        if not packages:
            ctk.CTkLabel(self._list_frame, text="No global packages found.", font=_font(13)).grid(row=0, column=0, pady=20)
            self._status_label.configure(text="Scan complete — nothing found.")
            self._scan_btn.configure(state="normal")
            return

        # Header row
        self._select_all_var = ctk.BooleanVar(value=False)
        select_all_cb = ctk.CTkCheckBox(
            self._list_frame, text="", font=_font(13),
            variable=self._select_all_var,
            command=self._on_select_all_toggle
        )
        select_all_cb.grid(row=0, column=0, padx=8, pady=4)

        for col, text in enumerate(["Manager", "Package", "Version", "Status"]):
            ctk.CTkLabel(
                self._list_frame, text=text, font=_font(13, "bold")
            ).grid(row=0, column=col + 1, sticky="w", padx=8, pady=4)

        self._row_status_labels.clear()
        for i, pkg in enumerate(packages, start=1):
            cb = ctk.CTkCheckBox(self._list_frame, text="", font=_font(13))
            cb.grid(row=i, column=0, padx=8)

            ctk.CTkLabel(self._list_frame, text=pkg.manager, font=_font(13)).grid(row=i, column=1, sticky="w", padx=8)
            ctk.CTkLabel(self._list_frame, text=pkg.name, font=_font(13)).grid(row=i, column=2, sticky="w", padx=8)
            ctk.CTkLabel(self._list_frame, text=pkg.version, font=_font(13)).grid(row=i, column=3, sticky="w", padx=8)

            status_lbl = ctk.CTkLabel(self._list_frame, text="", font=_font(13))
            status_lbl.grid(row=i, column=4, sticky="w", padx=8)
            self._row_status_labels[i] = status_lbl

            self._checkboxes.append((cb, pkg))

        self._status_label.configure(text=f"Found {len(packages)} globally installed package(s).")
        self._scan_btn.configure(state="normal")
        self._uninstall_btn.configure(state="normal")
        self._export_btn.configure(state="normal")

    def _log_append(self, text: str):
        self._log.configure(state="normal")
        self._log.insert("end", text)
        self._log.see("end")
        self._log.configure(state="disabled")
