# -*- coding: utf-8 -*-
"""
ҚУАН SUPER ЫҚШАМДАУ (Super Enhanced Edition)
Шығынсыз ZIP архиватор: архивтеу, қауіпсіз шығару, CRC бүтіндігін тексеру,
жалпы өлшемді есептеу және контекстік мәзір.
Тек Python стандартты кітапханаларын пайдаланады.
"""

import os
import zipfile
import threading
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path, PurePosixPath

APP_NAME = "ҚУАН SUPER ЫҚШАМДАУ"
GOLD = "#D6AD45"
BG = "#151515"
PANEL = "#222222"
TEXT = "#F4F0E6"
MUTED = "#B9B2A3"
DARK_ENTRY = "#111111"


class QuanZipApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("900x680")
        self.root.minsize(760, 580)
        self.root.configure(bg=BG)

        self.selected: list[Path] = []
        self.busy = False

        self._setup_style()
        self._build_ui()
        self._setup_context_menu()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Gold.Horizontal.TProgressbar",
            troughcolor="#3A3A3A",
            background=GOLD,
            bordercolor="#3A3A3A",
            lightcolor=GOLD,
            darkcolor=GOLD,
        )

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(18, 4))

        tk.Label(
            header, text="ҚУАН", bg=BG, fg=GOLD,
            font=("Segoe UI", 26, "bold")
        ).pack(anchor="w")
        tk.Label(
            header, text="SUPER ЫҚШАМДАУ v2.0",
            bg=BG, fg=TEXT, font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Шығынсыз архивтеу  •  Қауіпсіз шығару  •  CRC бүтіндігі  •  Жылдам басқару",
            bg=BG, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 0))

        # Main card
        card = tk.Frame(
            self.root, bg=PANEL,
            highlightbackground="#4B4028", highlightthickness=1
        )
        card.pack(fill="both", expand=True, padx=24, pady=12)

        # Top buttons
        top_btns = tk.Frame(card, bg=PANEL)
        top_btns.pack(fill="x", padx=18, pady=(14, 6))

        self._button(top_btns, "＋ Файл қосу", self.add_files).pack(side="left", padx=(0, 6))
        self._button(top_btns, "▣ Папка қосу", self.add_folder).pack(side="left", padx=6)
        self._button(top_btns, "📁 Орналасқан жерін ашу", self.open_selected_location, secondary=True).pack(side="left", padx=6)
        self._button(top_btns, "− Жою", self.remove_selected, secondary=True).pack(side="left", padx=6)
        self._button(top_btns, "Тазарту", self.clear_list, secondary=True).pack(side="right")

        # Listbox + scrollbar
        list_frame = tk.Frame(card, bg=PANEL)
        list_frame.pack(fill="both", expand=True, padx=18, pady=4)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame,
            bg=DARK_ENTRY,
            fg=TEXT,
            selectbackground="#70591F",
            selectforeground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            height=12,
            activestyle="none",
            yscrollcommand=scrollbar.set,
            highlightthickness=0,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Key bindings & Double click
        self.listbox.bind("<Delete>", lambda e: self.remove_selected())
        self.listbox.bind("<BackSpace>", lambda e: self.remove_selected())
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_selected_location())

        # Action buttons
        actions = tk.Frame(card, bg=PANEL)
        actions.pack(fill="x", padx=18, pady=10)

        self._button(actions, "📦  ZIP-ке ықшамдау", self.create_zip).pack(
            side="left", fill="x", expand=True, padx=(0, 6), ipady=8
        )
        self._button(actions, "📂  ZIP-тен шығару", self.extract_zip).pack(
            side="left", fill="x", expand=True, padx=6, ipady=8
        )
        self._button(actions, "✓  Архивті тексеру", self.test_zip, secondary=True).pack(
            side="left", fill="x", expand=True, padx=(6, 0), ipady=8
        )

        # Progress + status
        self.progress = ttk.Progressbar(
            card, style="Gold.Horizontal.TProgressbar", mode="indeterminate"
        )
        self.progress.pack(fill="x", padx=18, pady=(2, 2))

        self.status = tk.StringVar(value="Дайын. Файл немесе папка таңдаңыз.")
        tk.Label(
            card, textvariable=self.status, bg=PANEL, fg=MUTED,
            anchor="w", font=("Segoe UI", 9)
        ).pack(fill="x", padx=18, pady=(2, 12))

        # Footer
        footer = tk.Label(
            self.root,
            text="Ескерту: Қысу сапасы жоғалмайды (Lossless). Тізімдегі элементті екі рет шерту арқылы папкасын ашуға болады.",
            bg=BG, fg=MUTED, wraplength=850, justify="left",
            font=("Segoe UI", 9)
        )
        footer.pack(fill="x", padx=26, pady=(0, 10))

    def _setup_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=PANEL, fg=TEXT, activebackground=GOLD, activeforeground="#17130A")
        self.context_menu.add_command(label="📁 Файлды/папканы ашу", command=self.open_selected_location)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="− Тізімнен жою", command=self.remove_selected)
        self.context_menu.add_command(label="🗑️ Тізімді толық тазарту", command=self.clear_list)

        self.listbox.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        try:
            index = self.listbox.nearest(event.y)
            if index >= 0 and not self.listbox.selection_includes(index):
                self.listbox.selection_clear(0, "end")
                self.listbox.selection_set(index)
                self.listbox.activate(index)
            if self.listbox.curselection():
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _button(self, parent, text, command, secondary=False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#34302A" if secondary else GOLD,
            fg=TEXT if secondary else "#17130A",
            activebackground="#E8C66B",
            activeforeground="#17130A",
            relief="flat",
            bd=0,
            padx=12,
            pady=7,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        )

    # ───────────────────── List & Size Management ─────────────────────

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Архивке қосылатын файлдарды таңдаңыз")
        self._add_paths(paths)

    def add_folder(self):
        path = filedialog.askdirectory(title="Архивке қосылатын папканы таңдаңыз")
        if path:
            self._add_paths([path])

    def _add_paths(self, paths):
        added = 0
        for item in paths:
            p = Path(item)
            if p.exists() and p not in self.selected:
                self.selected.append(p)
                self.listbox.insert("end", str(p))
                added += 1
        if added:
            self._update_status_info()
        else:
            self.status.set("Жаңа элемент қосылмады (қайталанатындар өткізілді).")

    def remove_selected(self):
        selection = list(self.listbox.curselection())
        if not selection:
            return
        for idx in reversed(selection):
            self.listbox.delete(idx)
            del self.selected[idx]
        self._update_status_info()

    def clear_list(self):
        self.selected.clear()
        self.listbox.delete(0, "end")
        self.status.set("Тізім тазартылды.")

    def open_selected_location(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning(APP_NAME, "Таңдалған элемент жоқ.")
            return
        idx = selection[0]
        path = self.selected[idx]
        try:
            target_path = path if path.is_dir() else path.parent
            if platform.system() == "Windows":
                os.startfile(target_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(target_path)])
            else:
                subprocess.run(["xdg-open", str(target_path)])
        except Exception as e:
            messagebox.showerror("Қате", f"Папканы ашу мүмкін болмады:\n{e}")

    def _update_status_info(self):
        total_items = len(self.selected)
        total_size = 0
        for p in self.selected:
            if p.is_file():
                try:
                    total_size += p.stat().st_size
                except Exception:
                    pass
            elif p.is_dir():
                for root_dir, _, files in os.walk(p):
                    for f in files:
                        fp = Path(root_dir) / f
                        try:
                            total_size += fp.stat().st_size
                        except Exception:
                            pass
        
        size_str = f"{total_size / (1024*1024):.2f} МБ" if total_size < 1024*1024*1024 else f"{total_size / (1024*1024*1024):.2f} ГБ"
        self.status.set(f"Таңдалған элементтер: {total_items}  |  Жалпы бастапқы көлемі: {size_str}")

    # ───────────────────── Worker helpers ─────────────────────

    def _run_worker(self, title: str, work):
        if self.busy:
            messagebox.showwarning(APP_NAME, "Қазір басқа операция жүріп жатыр. Күтіңіз.")
            return
        self.busy = True
        self.progress.start(12)
        self.status.set(title)

        def runner():
            try:
                result = work()
                self.root.after(0, lambda: self._finish(True, result))
            except Exception as exc:
                self.root.after(0, lambda e=str(exc): self._finish(False, e))

        threading.Thread(target=runner, daemon=True).start()

    def _finish(self, ok: bool, message: str):
        self.progress.stop()
        self.busy = False
        self.status.set(str(message).split("\n")[0])
        if ok:
            messagebox.showinfo(APP_NAME, str(message))
        else:
            messagebox.showerror("Қате", str(message))

    # ───────────────────── ZIP Slip protection ─────────────────────

    @staticmethod
    def _safe_target(base: Path, member: zipfile.ZipInfo) -> Path:
        """ZIP Slip шабуылынан қорғаныс."""
        name = member.filename.replace("\\", "/")
        pure = PurePosixPath(name)

        if pure.is_absolute() or any(part == ".." for part in pure.parts):
            raise ValueError(f"Қауіпті архив жолы анықталды: {member.filename}")

        target = (base / Path(*pure.parts)).resolve()
        base_resolved = base.resolve()

        if target != base_resolved and base_resolved not in target.parents:
            raise ValueError(f"Рұқсат етілмеген жол: {member.filename}")

        return target

    # ───────────────────── Core operations ─────────────────────

    def create_zip(self):
        if not self.selected:
            messagebox.showwarning(APP_NAME, "Алдымен файл немесе папка қосыңыз.")
            return

        destination = filedialog.asksaveasfilename(
            title="ZIP архивін сақтау",
            defaultextension=".zip",
            filetypes=[("ZIP архиві", "*.zip")],
            initialfile="QUAN_SUPER_ARCHIVE.zip",
        )
        if not destination:
            return

        sources = [p.resolve() for p in self.selected]
        destination_path = Path(destination)

        def work():
            total_source_size = 0
            with zipfile.ZipFile(
                destination_path,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
                allowZip64=True,
            ) as zf:
                for source in sources:
                    if source.is_file():
                        total_source_size += source.stat().st_size
                        zf.write(source, source.name)

                    elif source.is_dir():
                        base_name = source.name.rstrip("/\\")
                        zf.writestr(base_name + "/", b"")

                        for current, dirs, files in os.walk(source):
                            current_path = Path(current)
                            rel = current_path.relative_to(source.parent)

                            if not dirs and not files:
                                zf.writestr(rel.as_posix().rstrip("/") + "/", b"")

                            for filename in files:
                                file_path = current_path / filename
                                if file_path.is_symlink():
                                    continue
                                try:
                                    total_source_size += file_path.stat().st_size
                                except Exception:
                                    pass
                                arcname = file_path.relative_to(source.parent).as_posix()
                                zf.write(file_path, arcname)

            # CRC тексеру
            with zipfile.ZipFile(destination_path, "r") as check:
                bad = check.testzip()
                if bad:
                    raise RuntimeError(f"Архив тексеруден өтпеді: {bad}")

            archive_size = destination_path.stat().st_size
            ratio = ((total_source_size - archive_size) / total_source_size * 100) if total_source_size > 0 else 0

            size_mb = archive_size / (1024 * 1024)
            return (
                f"Архив сәтті жасалды!\n"
                f"Орны: {destination_path}\n"
                f"Архив көлемі: {size_mb:.2f} МБ (Қысылуы: {ratio:.1f}%)\n"
                f"CRC бүтіндігі тексерілді."
            )

        self._run_worker("ZIP архиві максималды деңгейде жасалып жатыр…", work)

    def extract_zip(self):
        archive = filedialog.askopenfilename(
            title="ZIP архивін таңдаңыз",
            filetypes=[("ZIP архиві", "*.zip")],
        )
        if not archive:
            return

        destination = filedialog.askdirectory(title="Қай папкаға шығару керек?")
        if not destination:
            return

        archive_path = Path(archive)
        output_dir = Path(destination)

        if any(output_dir.iterdir()):
            if not messagebox.askyesno(
                APP_NAME,
                "Таңдалған папка бос емес.\n"
                "Файлдар қайта жазылуы мүмкін. Жалғастыру керек пе?",
            ):
                return

        def work():
            with zipfile.ZipFile(archive_path, "r") as zf:
                bad = zf.testzip()
                if bad:
                    raise RuntimeError(f"Архив бүлінген немесе CRC қатесі бар: {bad}")

                extracted = 0
                for info in zf.infolist():
                    target = self._safe_target(output_dir, info)

                    if info.is_dir() or info.filename.endswith("/"):
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info, "r") as src, open(target, "wb") as dst:
                            while True:
                                chunk = src.read(1024 * 1024)
                                if not chunk:
                                    break
                                dst.write(chunk)
                        extracted += 1

            return (
                f"Шығару сәтті аяқталды!\n"
                f"Орны: {output_dir}\n"
                f"Шығарылған файлдар саны: {extracted}\n"
                f"Қауіпсіздік тексеруі (ZIP Slip) сәтті өтті."
            )

        self._run_worker("Архив қауіпсіз шығарылып жатыр…", work)

    def test_zip(self):
        archive = filedialog.askopenfilename(
            title="Тексерілетін ZIP архивін таңдаңыз",
            filetypes=[("ZIP архиві", "*.zip")],
        )
        if not archive:
            return

        def work():
            with zipfile.ZipFile(archive, "r") as zf:
                bad = zf.testzip()
                if bad:
                    raise RuntimeError(f"Тексеру сәтсіз: бүлінген файл — {bad}")

                infos = zf.infolist()
                total_files = sum(1 for i in infos if not (i.is_dir() or i.filename.endswith("/")))
                total_dirs = len(infos) - total_files
                compressed_size = sum(i.compress_size for i in infos)
                uncompressed_size = sum(i.file_size for i in infos)

            return (
                f"Архив толығымен бүтін және дұрыс!\n"
                f"CRC тексеруі сәтті өтті.\n"
                f"Файлдар: {total_files} | Папкалар: {total_dirs}\n"
                f"Қысылған көлемі: {compressed_size / (1024*1024):.2f} МБ (Бастапқысы: {uncompressed_size / (1024*1024):.2f} МБ)"
            )

        self._run_worker("Архивтің CRC бүтіндігі тексеріліп жатыр…", work)


def main():
    root = tk.Tk()
    QuanZipApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()