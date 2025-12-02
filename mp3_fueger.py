"""
mp3_fueger.py
GUI‑Tool zum Zusammenfügen von MP3‑Dateien mit pydub und tkinter.
"""

import os
import re
import sys
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment


def ensure_ffmpeg() -> bool:
    """
    Prüft, ob ffmpeg vorhanden ist.
    Falls nicht, wird versucht, ffmpeg via winget zu installieren.
    """
    if shutil.which("ffmpeg"):
        return True

    messagebox.showinfo(
        "Hinweis",
        "ffmpeg wurde nicht gefunden.\n\n"
        "Es wird versucht, ffmpeg mit winget zu installieren.\n"
        "Bitte bestätigen Sie ggf. die Windows-Meldung mit 'Ja'."
    )

    try:
        subprocess.run(
            ["powershell", "-Command",
             "winget install --id=Gyan.FFmpeg -e --source=winget"],
            check=True
        )
        return shutil.which("ffmpeg") is not None
    except subprocess.SubprocessError as err:
        messagebox.showerror("Fehler", f"ffmpeg konnte nicht installiert werden:\n{err}")
        return False


def numeric_sort_key(filename: str) -> int:
    """
    Extrahiert die erste Zahl aus dem Dateinamen für die Sortierung.
    Gibt die Zahl zurück, ansonsten den Dateinamen in Kleinbuchstaben.
    """
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return filename.lower()


class MP3MergerApp:
    """GUI‑Klasse zum Laden, Sortieren und Zusammenfügen von MP3‑Dateien."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialisiert die GUI‑Elemente für eine Merger‑Instanz."""
        self.root = root
        self.root.title("MP3 Merger Instanz")
        self.files: list[str] = []

        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=60, height=20)
        self.listbox.pack(padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Ordner öffnen",
                  command=self.load_folder).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Nach oben",
                  command=self.move_up).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Nach unten",
                  command=self.move_down).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Zusammenfügen",
                  command=self.start_merge).grid(row=0, column=3, padx=5)

        tk.Label(root, text="Zusammenfügen:").pack()
        self.progress_merge = ttk.Progressbar(
            root, orient="horizontal", length=400, mode="determinate"
        )
        self.progress_merge.pack(pady=5)

        tk.Label(root, text="Export:").pack()
        self.progress_export = ttk.Progressbar(
            root, orient="horizontal", length=400, mode="indeterminate"
        )
        self.progress_export.pack(pady=5)

    def load_folder(self) -> None:
        """Lädt alle MP3‑Dateien aus einem ausgewählten Ordner in die Liste."""
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.files = [
            os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".mp3")
        ]
        self.files.sort(key=lambda f: numeric_sort_key(os.path.basename(f)))
        self.listbox.delete(0, tk.END)
        for f in self.files:
            self.listbox.insert(tk.END, os.path.basename(f))

    def move_up(self) -> None:
        """Verschiebt die ausgewählte Datei eine Position nach oben."""
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx == 0:
            return
        self.files[idx - 1], self.files[idx] = self.files[idx], self.files[idx - 1]
        self.refresh_listbox(idx - 1)

    def move_down(self) -> None:
        """Verschiebt die ausgewählte Datei eine Position nach unten."""
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx == len(self.files) - 1:
            return
        self.files[idx + 1], self.files[idx] = self.files[idx], self.files[idx + 1]
        self.refresh_listbox(idx + 1)

    def refresh_listbox(self, new_idx: int) -> None:
        """Aktualisiert die Listbox nach einer Verschiebung."""
        self.listbox.delete(0, tk.END)
        for f in self.files:
            self.listbox.insert(tk.END, os.path.basename(f))
        self.listbox.select_set(new_idx)

    def start_merge(self) -> None:
        """Startet den Merge‑Prozess in einem Hintergrundthread."""
        if not self.files:
            messagebox.showwarning("Warnung", "Keine Dateien geladen!")
            return
        output = filedialog.asksaveasfilename(
            defaultextension=".mp3", filetypes=[("MP3 Dateien", "*.mp3")]
        )
        if not output:
            return
        threading.Thread(target=self.merge_files, args=(output,), daemon=True).start()

    def merge_files(self, output: str) -> None:
        """Fügt die geladenen MP3‑Dateien zusammen und exportiert sie."""
        combined = AudioSegment.empty()
        total = len(self.files)
        self.progress_merge["maximum"] = total
        self.progress_merge["value"] = 0

        for i, f in enumerate(self.files, start=1):
            try:
                audio = AudioSegment.from_file(f, format="mp3")
                combined += audio
            except Exception as err:  # pylint: disable=broad-exception-caught
                print(f"Überspringe {f}, konnte nicht dekodieren: {err}")
            self.root.after(0, lambda val=i: self.progress_merge.config(value=val))

        if len(combined) == 0:
            self.root.after(
                0, lambda: messagebox.showerror("Fehler", "Keine gültigen MP3-Dateien gefunden!")
            )
            return

        self.root.after(0, self.progress_export.start)
        combined.export(output, format="mp3")
        self.root.after(0, self.progress_export.stop)
        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "Fertig", f"Dateien wurden erfolgreich zusammengefügt:\n{output}"
            )
        )


class MainApp:
    """Hauptfenster für die MP3‑Merger‑App."""
    # pylint: disable=too-few-public-methods

    def __init__(self, root: tk.Tk) -> None:
        """Initialisiert das Hauptfenster und startet die erste Instanz."""
        self.root = root
        self.root.title("MP3 Merger Hauptfenster")

        tk.Button(root, text="Neue Instanz öffnen",
                  command=self.open_new_instance).pack(pady=10)

        self.open_new_instance()

    def open_new_instance(self) -> None:
        """Öffnet eine neue Merger‑Instanz in einem Toplevel‑Fenster."""
        new_win = tk.Toplevel(self.root)
        MP3MergerApp(new_win)


if __name__ == "__main__":
    root_window = tk.Tk()
    root_window.withdraw()

    if not ensure_ffmpeg():
        sys.exit("ffmpeg ist erforderlich, konnte aber nicht installiert werden.")

    root_window.deiconify()
    app = MainApp(root_window)
    root_window.mainloop()
