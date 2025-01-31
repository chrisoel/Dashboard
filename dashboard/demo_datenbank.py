import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../dashboard')))

import shutil
import random
from datetime import date, timedelta
from pathlib import Path

from datenbank_zugriff import DatenbankZugriff

def zufaelliges_datum(start: date, end: date) -> str:
    """
    Gibt ein zufälliges Datum (YYYY-MM-DD) zwischen `start` und `end` zurück.
    """
    delta = end - start
    tage = random.randint(0, delta.days)
    zufalls_datum = start + timedelta(days=tage)
    return zufalls_datum.isoformat()

def setup_demo_database(db_path="data/datenbank.db"):
    """
    Ersetzt eine vorhandene 'datenbank.db' durch eine neu erstellte
    und füllt sie mit zufälligen Beispiel-Daten.
    """
    db_file = Path(db_path)
    
    # 1) Vorhandene DB sichern (oder löschen)
    if db_file.exists():
        backup_file = db_file.parent / "datenbank_backup.db"
        print(f"[INFO] Alte Datenbank wird umbenannt in: {backup_file}")
        if backup_file.exists():
            backup_file.unlink()  # vorhandenes Backup löschen
        db_file.rename(backup_file)
    
    # 2) Neue DB erstellen und initialisieren
    print("[INFO] Lege neue Demo-Datenbank an...")
    datenbank = DatenbankZugriff(db_pfad=str(db_file))
    datenbank.starten()  # ruft intern 'verbinden()' + 'initialisieren()' auf
    
    # 3) Beispiel-Studiengang einfügen
    print("[INFO] Füge Beispiel-Studiengang 'Informatik' hinzu...")
    datenbank.studiengang_speichern(
        studiengang_name="Informatik",
        startdatum="2023-10-01",
        urlaubssemester=0,
        zeitmodell="Vollzeit"
    )
    
    # Aktuelle StudiengangID ermitteln (uniqueConstraint=1)
    sg_id = datenbank.abfragen(
        "SELECT studiengangID FROM studiengang WHERE uniqueConstraint = 1"
    )[0][0]
    
    # 4) Semester vorbereiten (legt bis zu 12 Semester an)
    print("[INFO] Erstelle Semester 1-12...")
    datenbank.semester_vorbereiten(sg_id)
    
    # 5) Zufällige Module anlegen
    modul_namen = [
        "Programmieren I", "Mathematik I", "Datenbanken", "Lineare Algebra",
        "Statistik", "Programmieren II", "KI Grundlagen", "Webentwicklung",
        "Operative Systeme", "Software-Engineering", "Data Science",
        "Projektmanagement", "IT-Security", "Machine Learning"
    ]
    modul_kuerzel_prefix = ["PRG", "DB", "MAT", "KI", "WEB", "ML", "SEC", "ALGO", "PM"]
    status_liste = ["Offen", "In Bearbeitung", "Abgeschlossen"]
    ects_werte = [5, 10, 15, 20]  # Muss %5=0 laut YAML
    
    # Wir fügen z.B. 15 zufällige Module ein
    anzahl_module = 15
    for i in range(anzahl_module):
        # Zufälliges Semester aus 1-12
        semester_id = random.randint(1, 12)
        # Zufälliger Name aus Liste
        modul_name = random.choice(modul_namen)
        # Erzeuge kleines Kürzel (z.B. "PRG103")
        kuerzel = random.choice(modul_kuerzel_prefix) + str(random.randint(100, 999))
        # Zufälliger Status
        status = random.choice(status_liste)
        # Zufällige ECTS
        ects = random.choice(ects_werte)
        # Zufälliges Startdatum zwischen 2023-10-01 und 2024-06-01
        startdatum = zufaelliges_datum(date(2023,10,1), date(2024,6,1))
        
        datenbank.modul_speichern(
            semester_id=semester_id,
            modul_name=modul_name,
            kuerzel=kuerzel,
            status=status,
            ects=ects,
            startdatum=startdatum
        )

    # 6) Prüfungsleistungen für abgeschlossene Module
    # Hole alle abgeschlossenen Module
    abgeschlossene_module = datenbank.abfragen(
        "SELECT modulID FROM modul WHERE modulStatus = 'Abgeschlossen';"
    )
    for (modul_id,) in abgeschlossene_module:
        # Erzeuge zufälliges Prüfungsdatum nach dem Modulstart
        # Erst Modulstart abfragen
        start_str = datenbank.abfragen(
            "SELECT modulStart FROM modul WHERE modulID = ?;", (modul_id,)
        )[0][0]
        start_year, start_month, start_day = map(int, start_str.split("-"))
        start_datum = date(start_year, start_month, start_day)
        # Prüfungsdatum zufällig zwischen Modulstart + 10 Tage und Modulstart + 120 Tage
        pruefung_datum = zufaelliges_datum(
            start_datum + timedelta(days=10),
            start_datum + timedelta(days=120)
        )
        # Ergebnis (0 - 100%)
        pruefung_ergebnis = random.randint(50, 100)  # Abgeschlossen => gutes Ergebnis
        
        # Einfügen
        datenbank.manipulieren(
            "INSERT INTO pruefungsleistung (modulID, pruefungDatum, pruefungErgebnis) VALUES (?, ?, ?)",
            (modul_id, pruefung_datum, pruefung_ergebnis)
        )
    
    # 7) (Optional) Verlaufs-Eintrag aktualisieren
    print("[INFO] Aktualisiere Studienfortschritts-Verlauf für heute...")
    datenbank.aktualisiere_studienfortschritt()

    # Datenbankverbindung beenden
    datenbank.trennen()
    print("[INFO] Demo-Datenbank erfolgreich erstellt.")

def main():
    setup_demo_database()

if __name__ == "__main__":
    main()