# tests/test_logik.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../dashboard')))

import pytest
from pathlib import Path

from dashboard.logik import Logik

@pytest.fixture(scope="function")
def logik_test():
    """Fixture zum Erstellen einer frischen Logik-Instanz für jeden Test."""
    test_db_pfad = "data/test_datenbank.db"

    # Entferne ggf. alte Test-Datenbank
    if Path(test_db_pfad).exists():
        Path(test_db_pfad).unlink()

    # Erstelle eine neue Instanz der Logik-Schicht
    logik = Logik(db_pfad=test_db_pfad)
    logik.starten()

    yield logik  # liefert die Logik-Instanz an den jeweiligen Test

    # Aufräumen nach Test
    logik.beenden()
    if Path(test_db_pfad).exists():
        Path(test_db_pfad).unlink()


def test_logik_verbindung(logik_test):
    """Testet, ob die Logik-Schicht erfolgreich gestartet wird."""
    assert logik_test.datenbank.verbindung is not None, \
        "Die Verbindung zur Datenbank sollte bestehen."


def test_view_erstellung(logik_test):
    """
    Testet, ob die in ansichten.yaml definierten Views (z.B. startbildschirm) korrekt erstellt werden.
    """
    # Nach dem Start sollte bereits initialisiert sein,
    # falls du "initialisieren()" nur bei Datenbankstart machst:
    # Ggf. nochmal manuell aufrufen, um sicherzugehen:
    logik_test.datenbank.initialisieren()

    # Jetzt schauen, ob "startbildschirm" existiert
    result = logik_test.datenbank.abfragen(
        "SELECT name FROM sqlite_master WHERE type='view' AND name='startbildschirm';"
    )
    assert len(result) == 1, "Die View 'startbildschirm' sollte existieren."


def test_startbildschirm_daten_speichern_und_lesen(logik_test):
    """
    Testet, ob Studiengangsdaten gespeichert und über die Ansicht 'startbildschirm' wieder ausgelesen werden können.
    """
    # 1) Studiengangdaten speichern
    daten = ("Informatik", "2022-10-01", 0, "Vollzeit")
    erfolg = logik_test.set_startbildschirm_ansicht_daten(daten)
    assert erfolg, "Das Speichern des Studiengangs sollte erfolgreich sein."

    # 2) Daten über View abfragen
    ergebnis = logik_test.get_startbildschirm_ansicht_daten()
    assert len(ergebnis) == 1, "In der View 'startbildschirm' sollte genau 1 Eintrag sein."
    assert ergebnis[0][0] == "Informatik", "Der Studiengang-Name sollte 'Informatik' sein."


def test_modul_insert_und_lesen_ueber_moduluebersicht(logik_test):
    """
    Testet, ob ein Modul angelegt und über die Ansicht 'moduluebersicht' abgefragt werden kann.
    """
    # Datenbank-Struktur anlegen
    logik_test.datenbank.initialisieren()

    # Zuerst: Studiengang speichern (damit wir SemesterID über 'semester_vorbereiten' haben)
    logik_test.datenbank.manipulieren("""
        INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, zeitModell, uniqueConstraint)
        VALUES (?, ?, ?, ?, ?);
    """, ("Informatik", "2022-10-01", 0, "Vollzeit", 1))

    # Hole studiengangID
    studiengang_id = logik_test.datenbank.abfragen("SELECT studiengangID FROM studiengang;")[0][0]

    # Semester anlegen (die Methode semester_vorbereiten legt 1..12 an)
    logik_test.datenbank.semester_vorbereiten(studiengang_id)

    # Nun existiert mindestens SemesterID = 1 => Wir fügen ein Modul ein:
    # set_moduluebersicht_ansicht_daten("INSERT", (semester_id, modul_name, kuerzel, status, ects, startdatum))
    erfolg = logik_test.set_moduluebersicht_ansicht_daten(
        "INSERT",
        (1, "Softwareentwicklung", "SE1", "Offen", 5, "2023-10-01")
    )
    assert erfolg, "Das Einfügen des Moduls sollte erfolgreich sein."

    # Jetzt über die View 'moduluebersicht' abfragen
    ergebnis = logik_test.get_moduluebersicht_ansicht_daten()
    assert len(ergebnis) == 1, "Es sollte genau ein Modul in der 'moduluebersicht' stehen."
    # Spalten in 'moduluebersicht' sind laut ansichten.yaml:
    # (m.modulID, s.semesterNR, m.modulName, m.modulKuerzel, m.modulStatus, m.modulEctsPunkte, m.modulStart)
    assert ergebnis[0][2] == "Softwareentwicklung", "Der Modulname sollte 'Softwareentwicklung' sein."
    assert ergebnis[0][3] == "SE1", "Das Kürzel sollte 'SE1' sein."


def test_modul_update(logik_test):
    """
    Testet das Aktualisieren eines vorhandenen Moduls über die Logik-Schicht.
    """
    logik_test.datenbank.initialisieren()

    # Studiengang und Semester anlegen
    logik_test.datenbank.manipulieren("""
        INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, zeitModell, uniqueConstraint)
        VALUES (?, ?, ?, ?, ?);
    """, ("Informatik", "2022-10-01", 0, "Vollzeit", 1))
    studiengang_id = logik_test.datenbank.abfragen("SELECT studiengangID FROM studiengang;")[0][0]
    logik_test.datenbank.semester_vorbereiten(studiengang_id)

    # Modul anlegen
    logik_test.set_moduluebersicht_ansicht_daten(
        "INSERT",
        (1, "Softwareentwicklung", "SE1", "Offen", 5, "2023-10-01")
    )
    # modulID ermitteln
    modul_id = logik_test.datenbank.abfragen("SELECT modulID FROM modul;")[0][0]

    # Modul aktualisieren: 
    # set_moduluebersicht_ansicht_daten("UPDATE", (modul_id, modul_name, kuerzel, status, ects, startdatum))
    erfolg = logik_test.set_moduluebersicht_ansicht_daten(
        "UPDATE",
        (modul_id, "Softwareentwicklung II", "SE2", "Abgeschlossen", 10, "2023-12-01")
    )
    assert erfolg, "Das Aktualisieren des Moduls sollte erfolgreich sein."

    # Über die View prüfen
    result = logik_test.get_moduluebersicht_ansicht_daten()
    assert len(result) == 1, "Es sollte nur das eine Modul geben."
    assert result[0][2] == "Softwareentwicklung II", "Der Modulname sollte aktualisiert sein."
    assert result[0][3] == "SE2", "Das Kürzel sollte aktualisiert sein."
    assert result[0][4] == "Abgeschlossen", "Der Status sollte auf 'Abgeschlossen' geändert sein."
    assert result[0][5] == 10, "ECTS sollten auf 10 aktualisiert worden sein."