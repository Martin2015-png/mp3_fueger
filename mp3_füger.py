import os
import re
import sys
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment

def ensure_ffmpeg():
    """Prüft ob ffmpeg vorhanden ist, sonst versucht Installation via winget."""
    if shutil.which("ffmpeg"):
        return True

    # Hinweisfenster anzeigen
    messagebox.showinfo(
        "Hinweis",
        "ffmpeg wurde nicht gefunden.\n\n"
        "Es wird versucht, ffmpeg mit winget zu installieren.\n"
        "Bitte bestätigen Sie ggf. die Windows-Meldung mit 'Ja'."
    )

    try:
        subprocess.run(
            ["powershell", "-Command", "winget install --id=Gyan.FFmpeg -e --source=winget"],
            check=True
        )
        return shutil.which("ffmpeg") is not None
    except Exception as e:
        messagebox.showerror("Fehler", f"ffmpeg konnte nicht installiert werden:\n{e}")
        return False

def numeric_sort_key(filename):
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return filename.lower()

class MP3MergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Merger mit Pydub")
        self.files = []

        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=60, height=20)
        self.listbox.pack(padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Ordner öffnen", command=self.load_folder).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Nach oben", command=self.move_up).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Nach unten", command=self.move_down).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Zusammenfügen", command=self.start_merge).grid(row=0, column=3, padx=5)

        # Fortschrittsbalken für Zusammenfügen
        tk.Label(root, text="Zusammenfügen:").pack()
        self.progress_merge = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_merge.pack(pady=5)

        # Fortschrittsbalken für Export
        tk.Label(root, text="Export:").pack()
        self.progress_export = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate")
        self.progress_export.pack(pady=5)

    def load_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".mp3")]
        self.files.sort(key=lambda f: numeric_sort_key(os.path.basename(f)))
        self.listbox.delete(0, tk.END)
        for f in self.files:
            self.listbox.insert(tk.END, os.path.basename(f))

    def move_up(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        if idx == 0: return
        self.files[idx-1], self.files[idx] = self.files[idx], self.files[idx-1]
        self.refresh_listbox(idx-1)

    def move_down(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        if idx == len(self.files)-1: return
        self.files[idx+1], self.files[idx] = self.files[idx], self.files[idx+1]
        self.refresh_listbox(idx+1)

    def refresh_listbox(self, new_idx):
        self.listbox.delete(0, tk.END)
        for f in self.files:
            self.listbox.insert(tk.END, os.path.basename(f))
        self.listbox.select_set(new_idx)

    def start_merge(self):
        if not self.files:
            messagebox.showwarning("Warnung", "Keine Dateien geladen!")
            return
        output = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 Dateien", "*.mp3")])
        if not output:
            return
        threading.Thread(target=self.merge_files, args=(output,), daemon=True).start()

    def merge_files(self, output):
        combined = AudioSegment.empty()
        total = len(self.files)
        self.progress_merge["maximum"] = total
        self.progress_merge["value"] = 0

        # Zusammenfügen
        for i, f in enumerate(self.files, start=1):
            try:
                audio = AudioSegment.from_file(f, format="mp3")
                combined += audio
            except Exception as e:
                print(f"Überspringe {f}, konnte nicht dekodieren: {e}")
            self.root.after(0, lambda val=i: self.progress_merge.config(value=val))

        if len(combined) == 0:
            self.root.after(0, lambda: messagebox.showerror("Fehler", "Keine gültigen MP3-Dateien gefunden!"))
            return

        # Export starten (indeterminate Balken läuft)
        self.root.after(0, self.progress_export.start)

        combined.export(output, format="mp3")

        # Export fertig
        self.root.after(0, self.progress_export.stop)
        self.root.after(0, lambda: messagebox.showinfo("Fertig", f"Dateien wurden erfolgreich zusammengefügt:\n{output}"))

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # GUI erst nach ffmpeg-Check zeigen

    if not ensure_ffmpeg():
        sys.exit("ffmpeg ist erforderlich, konnte aber nicht installiert werden.")

    root.deiconify()
    app = MP3MergerApp(root)
    root.mainloop()
