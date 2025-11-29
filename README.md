# mp3_fueger
Ein schlichter mp3_Datei Zusammenfüger...
MP3 Merger mit Pydub & Tkinter
Ein einfaches, aber robustes Tool zum Zusammenfügen von MP3‑Dateien mit einer grafischen Oberfläche. Das Projekt nutzt Python 3.13, Tkinter für die GUI und Pydub (mit ffmpeg) für die Audiobearbeitung. Es kann als .exe mit PyInstaller gebaut werden und läuft dann ohne installiertes Python.
WICHTIG: Es muss Python 3.13 oder niedriger genutzt werden, da sonst AudioSegment nicht genutzt werden kann
Unterstützt mehrere Instanzen
✨ Features
Grafische Oberfläche mit Dateiliste

Dateien per Knopfdruck nach oben/unten verschieben

Automatisches numerisches Sortieren (z. B. Track01, Track02 …)

Zwei Fortschrittsbalken:

Zusammenfügen

Export

Fehlerhafte MP3s werden übersprungen, ohne dass die App abstürzt

ffmpeg‑Check beim Start:

Falls ffmpeg fehlt, Hinweisfenster mit Info („Bitte ggf. Windows‑Meldung bestätigen“)

Automatische Installation via winget möglich

📦 Voraussetzungen
Python 3.13 (nur für Entwicklung/Build)

Abhängigkeiten:
Keine, bei Python-Nutzung diese:
pip install pydub audioop-lts
ffmpeg (wird beim Start geprüft und ggf. automatisch installiert)

🛠️ Nutzung
Als Python‑Skript
bash
python audifügextended.py
Als .exe (empfohlen)
 Und mit pyinstaller als exe

Starten → ffmpeg wird geprüft und ggf. automatisch installiert.


⚠️ Hinweise
Beim ersten Start kann Windows eine UAC‑Meldung anzeigen, wenn ffmpeg installiert werden muss. Bitte mit „Ja“ bestätigen.

Die .exe ist eigenständig und benötigt kein installiertes Python.

ffmpeg wird entweder automatisch installiert oder kann manuell ins gleiche Verzeichnis gelegt werden.

📜 Lizenz
Dieses Projekt ist frei nutzbar für private Zwecke. Für kommerzielle Nutzung bitte Lizenzbedingungen von Pydub und ffmpeg beachten.

