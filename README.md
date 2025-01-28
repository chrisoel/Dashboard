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
- Auseinandersetzung mit objektorientierter Programmierung in Python
- Entwicklung einer ersten Gesamtarchitektur

### 3. Finalisierungsphase
- Implementierung des Codes
- Dokumentation der Methodik und Ergebnisse.

---

## Installation und Nutzung

### Voraussetzungen
- Python 3.10 oder höher
- Bibliotheken: `Tkinter`, `SQLite3`, `pytest`

### Installation
1. Klone das Repository:
   ```bash
   git clone https://github.com/chrisoel/Dashboard.git

Hinweis: Es folgen noch weitere Anweisungen! Aktuell noch nicht funktionsfähig.