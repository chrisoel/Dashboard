#!/usr/bin/env python3
"""
Erstellt eine neue SQLite-Datenbank 'test_studienfortschritt.db' mit gleichem Tabellenaufbau 
(weniger Constraints) und füllt sie mit Zufallsdaten, damit man z.B. im Studienfortschritt 
eine mehrtägige Kurve sieht.
"""

import os
import sqlite3
import random
import datetime
from pathlib import Path

def erstelle_leere_db(db_path="test_studienfortschritt.db"):
    """Legt eine neue DB an und entfernt alte, falls vorhanden."""
    if Path(db_path).exists():
        os.remove(db_path)
    return sqlite3.connect(db_path)


def tabellen_erstellen_ohne_constraints(conn: sqlite3.Connection):
    """
    Erstellt Tabellen ähnlich deiner YAML-Definition, aber 
    mit vereinfachten Constraints. 
    (Beispielhaft für studiengang, verlauf, modul etc.)
    """
    cursor = conn.cursor()

    # Beispiel: Ohne UNIQUE bei 'uniqueConstraint' oder 'zeitpunkt'
    # Du kannst die Constraints anpassen, wie du sie "entschärfen" möchtest.

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS studiengang (
        studiengangID INTEGER PRIMARY KEY AUTOINCREMENT,
        studiengangName TEXT,
        startDatumStudium DATE,
        urlaubsSemester INTEGER,
        zeitModell TEXT,
        uniqueConstraint INTEGER DEFAULT 1 -- Removed UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verlauf (
        verlaufID INTEGER PRIMARY KEY AUTOINCREMENT,
        modulOffen INTEGER DEFAULT 0,
        modulInBearbeitung INTEGER DEFAULT 0,
        modulAbgeschlossen INTEGER DEFAULT 0,
        zeitpunkt DATE -- Removed UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS semester (
        semesterID INTEGER PRIMARY KEY AUTOINCREMENT,
        studiengangID INTEGER,
        semesterNR INTEGER,
        istUrlaubSemester INTEGER
        -- foreign key etc. entfernt, um constraints zu vermeiden
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modul (
        modulID INTEGER PRIMARY KEY AUTOINCREMENT,
        semesterID INTEGER,
        modulName TEXT,
        modulKuerzel TEXT,
        modulStatus TEXT,
        modulEctsPunkte INTEGER,
        modulStart DATE
    );
    """)

    conn.commit()


def beispieldaten_einfuegen(conn: sqlite3.Connection):
    """
    Fügt Beispiel- und Zufallsdaten in die Tabellen ein,
    damit u.a. 'verlauf' mehrere Zeilen für unterschiedliche Zeitpunkte hat.
    """
    cursor = conn.cursor()

    # 1) Studiengang-Dummy
    cursor.execute("""
        INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, zeitModell)
        VALUES (?, ?, ?, ?);
    """, ("Informatik", "2023-10-01", 0, "Vollzeit"))

    # 2) Zufallsdaten für 'verlauf' anlegen
    # Wir erzeugen z. B. 10 Einträge an 10 aufeinanderfolgenden Tagen
    startdatum = datetime.date(2023, 10, 1)
    for i in range(10):
        aktuelles_datum = startdatum + datetime.timedelta(days=i)
        modul_offen = random.randint(0, 10)
        modul_in_bearbeitung = random.randint(0, 5)
        modul_abgeschlossen = random.randint(0, 5)

        # Insert
        cursor.execute("""
            INSERT INTO verlauf (modulOffen, modulInBearbeitung, modulAbgeschlossen, zeitpunkt)
            VALUES (?, ?, ?, ?)
        """, (
            modul_offen,
            modul_in_bearbeitung,
            modul_abgeschlossen,
            aktuelles_datum.isoformat()
        ))

    # 3) Ein paar Semester
    for sem_nr in range(1, 6):
        cursor.execute("""
            INSERT INTO semester (studiengangID, semesterNR, istUrlaubSemester)
            VALUES (1, ?, 0)
        """, (sem_nr,))

    # 4) Ein paar Module - rein zufällig
    modul_namen = ["Mathe I", "Programmieren I", "Datenbanken", "Statistik", "Softwareentw."]
    status_liste = ["Offen", "In Bearbeitung", "Abgeschlossen"]
    for _ in range(8):
        sem = random.randint(1, 5)
        name = random.choice(modul_namen)
        kurz = name[:3].upper() + str(random.randint(100,999))
        ects = random.choice([5,10,15])
        status = random.choice(status_liste)
        startdt = (startdatum + datetime.timedelta(days=random.randint(0,60))).isoformat()

        cursor.execute("""
            INSERT INTO modul (semesterID, modulName, modulKuerzel, modulStatus, modulEctsPunkte, modulStart)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sem, name, kurz, status, ects, startdt))

    conn.commit()


def main():
    conn = erstelle_leere_db("test_studienfortschritt.db")
    try:
        tabellen_erstellen_ohne_constraints(conn)
        beispieldaten_einfuegen(conn)

        print("[INFO] Die neue DB 'test_studienfortschritt.db' wurde erstellt.")
        print("[INFO] Tabellen ohne strenge Constraints angelegt und Beispiel-/Zufallsdaten eingefügt.")
        print("[INFO] Du kannst jetzt dein Dashboard damit verbinden.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()