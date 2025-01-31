# IU Dashboard - Studienverlaufs- und Fortschrittsmanagement

## Projektübersicht

Dieses Projekt wurde im Rahmen des Portfolios "Dashboard" für die IU Internationale Hochschule entwickelt. Ziel ist es, ein Dashboard zu erstellen, das Studierenden eine zentrale Übersicht über ihren Studienverlauf, Fortschritte und offene Aufgaben bietet. Dabei werden fragmentierte Informationen wie Kursbuchungen, Notenübersicht und Studienablaufplan konsolidiert und benutzerfreundlich dargestellt.

---

## Zielsetzung

### Hauptziele:
- **Konsolidierung von Informationen:** Alle relevanten Modulinformationen, Prüfungsleistungen und Notenübersichten an einem zentralen Ort.
- **Messbarkeit des Fortschritts:** Darstellung des Studienfortschritts durch Visualisierung abgeschlossener und offener Module.
- **Verbesserung des Zeitmanagements:** Berechnung des täglichen Lernaufwands, um eine optimale Planung zu ermöglichen.

### Vorteile:
- Benutzerfreundlichkeit durch zentrale Übersicht.
- Zeitersparnis bei der Planung und Nachverfolgung von Studienaktivitäten.
- Unterstützung im Zeitmanagement, um ein fristgerechtes Studium zu gewährleisten.

---

## Architektur des Dashboards

Das Dashboard basiert auf einem **4-Schichten-Modell**, das eine klare Trennung der Verantwortlichkeiten ermöglicht:

1. **GUI-Schicht:** 
   - Die grafische Benutzeroberfläche ermöglicht eine einfache Navigation und Interaktion. Sie wird mit `Tkinter` entwickelt.
   - Kernklasse: `Dashboard`

2. **Logik-Schicht:** 
   - Diese Schicht verbindet die GUI mit der Datenbankzugriffsschicht und enthält Geschäftslogik, wie z. B. Datenmanipulation und -abfrage.
   - Kernklasse: `Logik`

3. **Datenbankzugriffsschicht:**
   - Kapselt alle Interaktionen mit der Datenbank und stellt eine sichere und strukturierte Schnittstelle bereit.
   - Kernklasse: `DatenbankZugriff`

4. **Datenbank-Schicht:** 
   - Speichert alle relevanten Informationen, darunter Studiengänge, Module, Semester und Prüfungsleistungen.
   - Technologie: `SQLite`

---

## Hauptfunktionen

1. **Startbildschirm:**
   - Übersicht über den aktuellen Studiengang.
   - Anzeige von verbleibenden Semestern und Modulen.

2. **Modulübersicht:**
   - Liste aller Module mit Status (offen, abgeschlossen).
   - Möglichkeit, Details eines Moduls abzurufen und Noten einzutragen.

3. **Studienfortschritt:**
   - Visualisierung des Studienfortschritts (z. B. Balkendiagramme).
   - Darstellung abgeschlossener und ausstehender Module.

4. **Zeitmanagement:**
   - Berechnung des Lernaufwands basierend auf der verbleibenden Zeit und den ECTS-Punkten.
   - Vorschläge zur Wochenplanung.

5. **Einstellungen:**
   - Anpassung der Ansicht und Verwaltung der Daten.

---

## Technologien

- **Python:** Hauptprogrammiersprache.
- **Tkinter:** Für die grafische Benutzeroberfläche.
- **SQLite:** Datenbanklösung für persistente Datenspeicherung.
- **Pytest:** Testframework zur Sicherstellung der Funktionalität.
- **Doxygen:** Automatische Dokumentationserstellung für den Code.

---

## Implementierungsdetails

### UML-Klassendiagramm
Das Dashboard basiert auf einem UML-Klassendiagramm, das die Entitäten `Studiengang`, `Semester`, `Modul` und `Prüfungsleistung` abbildet. Zusätzliche Attribute wie `startDatum` und `planEndDatum` wurden für die Zeitplanung ergänzt.

### Validierung
- **Datenbank:** Constraints wie `CHECK` und `FOREIGN KEYS` gewährleisten Datenkonsistenz.
- **Python-Klassen:** Validierung durch Setter, Getter und Property-Attribute (z. B. Überprüfung von Datumseingaben).

---

## Entwicklungsprozess

### 1. Konzeptionsphase
- Definition der Ziele und Anforderungen.
- Erstellung eines UML-Klassendiagramms.
- Auswahl der Technologien: `Python`, `Tkinter`, `SQLite`.

### 2. Erarbeitungsphase
- Auseinandersetzung mit objektorientierter Programmierung in Python.
- Entwicklung einer ersten Gesamtarchitektur.

### 3. Finalisierungsphase
- Implementierung des Codes.
- Dokumentation der Methodik und Ergebnisse.
- Erstellung einer Installationsanleitung und eines Abstracts.

---

## Installation und Nutzung

### Voraussetzungen
- Python 3.10 oder höher
- Virtuelle Umgebung empfohlen: `venv`
- Notwendige Bibliotheken sind in `requirements.txt` enthalten.

### Installation
1. **Repository klonen:**
   ```bash
   git clone https://github.com/chrisoel/Dashboard.git
   cd Dashboard
   ```
2. **Virtuelle Umgebung erstellen (optional, empfohlen):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Für macOS/Linux
   venv\Scripts\activate     # Für Windows
   ```
3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Dashboard starten:**
   ```bash
   python main.py
   ```

### Tests ausführen
```bash
pytest tests/
```

---

## Doxygen Dokumentation generieren

Falls `Doxygen` nicht installiert ist, muss es zuerst installiert werden:

- **Windows:** Über den Doxygen Installer oder `choco install doxygen`
- **MacOS:** `brew install doxygen`
- **Linux:** `sudo apt install doxygen`

### Generieren der Dokumentation
```bash
doxygen Doxyfile
```
Die generierte Dokumentation befindet sich anschließend im `docs/`-Verzeichnis.

---

## GitHub Repository & Finalisierung

### Projektstruktur
```plaintext
Dashboard/
├── src/                # Quellcode
├── tests/              # Unit Tests
├── docs/               # Automatisch generierte Doxygen-Dokumentation
├── data/               # Datenbank & YAML-Dateien
├── requirements.txt    # Abhängigkeiten
├── README.md           # Projektbeschreibung
├── Doxyfile            # Doxygen Konfiguration
└── .gitignore          # Dateien, die ignoriert werden sollen
```

### Wichtige Hinweise für die Abgabe
- **Das `docs/`-Verzeichnis wird aus dem Git-Repository ausgeschlossen.**
  ```bash
  echo "docs/" >> .gitignore
  ```
- **Das Repository ist öffentlich zugänglich oder für die Prüfer freigegeben.**
- **Die `requirements.txt` enthält nur die wirklich notwendigen Abhängigkeiten.**
- **Installationsanleitung und Abstract sind als PDFs beigefügt.**
- **Alle Daten sind als ZIP-Archiv für die Abgabe gepackt.**

---

## Autor
- **Chris Oel**
- IU Internationale Hochschule
- `chrisoel@iu-study.org`
