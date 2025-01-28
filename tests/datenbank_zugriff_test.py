import pytest
import sqlite3
from pathlib import Path
from dashboard.datenbank_zugriff import DatenbankZugriff

@pytest.fixture(scope="function")
def db_test():
    """Fixture zum Erstellen einer neuen Test-Datenbank für jeden Test."""
    test_db_pfad = "data/test_datenbank.db"

    # Entferne die alte Test-Datenbank, falls vorhanden
    if Path(test_db_pfad).exists():
        Path(test_db_pfad).unlink()

    # Erstelle neue Instanz des Datenbankzugriffs
    db = DatenbankZugriff(db_pfad=test_db_pfad)
    db.starten()
    yield db  # Bereitstellen

    # Test-Datenbank löschen
    db.trennen()
    if Path(test_db_pfad).exists():
        Path(test_db_pfad).unlink()


def test_verbindung_herstellen(db_test):
    """Testet, ob die Verbindung zur Datenbank hergestellt wird."""
    assert db_test.verbindung is not None, "Die Verbindung sollte nicht None sein."


def test_tabellen_erstellen(db_test):
    """Testet, ob Tabellen basierend auf YAML-Dateien erstellt werden."""
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='studiengang';"
    ergebnis = db_test.abfragen(sql)
    assert len(ergebnis) == 1, "Die Tabelle 'studiengang' sollte existieren."


def test_daten_einfuegen_und_abfragen(db_test):
    """Testet, ob Daten eingefügt und korrekt abgefragt werden können."""
    sql_insert = "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);"
    daten = ("Informatik", "2022-10-01", 0, "MO_DI_MI", "Vollzeit", 1)
    erfolg = db_test.manipulieren(sql_insert, daten)
    assert erfolg, "Das Einfügen von Daten sollte erfolgreich sein."

    sql_select = "SELECT studiengangName, startDatumStudium, urlaubsSemester FROM studiengang WHERE studiengangName = ?;"
    ergebnis = db_test.abfragen(sql_select, ("Informatik",))
    assert len(ergebnis) == 1, "Die Abfrage sollte genau einen Eintrag zurückgeben."
    assert ergebnis[0] == ("Informatik", "2022-10-01", 0), "Die abgefragten Daten stimmen nicht mit den eingefügten überein."


def test_fehlerhafte_abfrage(db_test):
    """Testet, ob fehlerhafte SQL-Abfragen korrekt behandelt werden."""
    with pytest.raises(sqlite3.Error):
        db_test.abfragen("SELECT * FROM nicht_existierende_tabelle;")

def test_mehrere_datensaetze_einfuegen_und_abfragen(db_test):
    """Testet das Einfügen und Abrufen mehrerer Datensätze."""
    daten = [
        ("Maschinenbau", "2023-04-01", 1, "MO_MI_FR", "TeilzeitI", 2),
        ("Elektrotechnik", "2021-10-01", 0, "DI_DO", "Vollzeit", 3)
    ]
    
    for eintrag in daten:
        assert db_test.manipulieren(
            "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
            eintrag
        )

    ergebnis = db_test.abfragen("SELECT COUNT(*) FROM studiengang;")
    assert ergebnis[0][0] == len(daten), "Die Anzahl der Einträge sollte mit der Anzahl der eingefügten übereinstimmen."

def test_on_delete_cascade(db_test):
    """Testet, ob das Löschen eines Studiengangs verbundene Semester löscht."""
    db_test.manipulieren(
        "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
        ("Test-Studiengang", "2022-10-01", 0, "MO_DI", "Vollzeit", 99)
    )
    studiengang_id = db_test.abfragen("SELECT studiengangID FROM studiengang WHERE uniqueConstraint = 99;")[0][0]

    db_test.manipulieren(
        "INSERT INTO semester (studiengangID, semesterNR, istUrlaubSemester) VALUES (?, ?, ?);",
        (studiengang_id, 1, 0)
    )

    db_test.manipulieren("DELETE FROM studiengang WHERE studiengangID = ?;", (studiengang_id,))

    ergebnis = db_test.abfragen("SELECT COUNT(*) FROM semester WHERE studiengangID = ?;", (studiengang_id,))
    assert ergebnis[0][0] == 0, "Das Semester sollte ebenfalls gelöscht werden (ON DELETE CASCADE)."

def test_unique_constraint(db_test):
    """Testet, ob das UNIQUE-Constraint für uniqueConstraint in studiengang funktioniert."""
    db_test.manipulieren(
        "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
        ("Medizintechnik", "2022-10-01", 0, "MO_DI", "Vollzeit", 42)
    )
    
    erfolg = db_test.manipulieren(
        "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
        ("Wirtschaftsinformatik", "2023-04-01", 1, "MO_MI", "TeilzeitI", 42)
    )
    
    assert not erfolg, "Das Einfügen sollte fehlschlagen, da uniqueConstraint UNIQUE ist."

def test_check_constraint_modulnote(db_test):
    """Testet, ob das CHECK-Constraint für modulNote greift."""

    db_test.manipulieren(
        "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
        ("Test-Studiengang", "2022-10-01", 0, "MO_DI", "Vollzeit", 99)
    )
    studiengang_id = db_test.abfragen("SELECT studiengangID FROM studiengang WHERE uniqueConstraint = 99;")[0][0]

    db_test.manipulieren(
        "INSERT INTO semester (studiengangID, semesterNR, istUrlaubSemester) VALUES (?, ?, ?);",
        (studiengang_id, 1, 0)
    )
    semester_id = db_test.abfragen("SELECT semesterID FROM semester WHERE studiengangID = ?;", (studiengang_id,))[0][0]

    erfolg = db_test.manipulieren(
        "INSERT INTO modul (semesterID, modulName, modulKuerzel, modulStatus, modulPruefungsform, modulNote, modulEctsPunkte, modulStart) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        (semester_id, "Mathematik", "MATH1", "Offen", "Klausur", 2.3, 5, "2024-04-01")
    )
    assert erfolg, "Das Einfügen einer gültigen Note sollte funktionieren."

    erfolg_falsch = db_test.manipulieren(
        "INSERT INTO modul (semesterID, modulName, modulKuerzel, modulStatus, modulPruefungsform, modulNote, modulEctsPunkte, modulStart) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        (semester_id, "Physik", "PHYS1", "Offen", "Klausur", 6.0, 5, "2024-04-01")
    )
    assert not erfolg_falsch, "Das Einfügen einer Note außerhalb des Bereichs 1.0 - 5.0 sollte fehlschlagen."

def test_trennen_und_erneutes_verbinden(db_test):
    """Testet, ob die Datenbankverbindung korrekt geschlossen und wiederhergestellt wird."""
    db_test.trennen()
    assert db_test.verbindung is None, "Die Verbindung sollte nach trennen() None sein."

    db_test.verbinden()
    assert db_test.verbindung is not None, "Die Verbindung sollte nach verbinden() wiederhergestellt sein."

def test_sql_injection(db_test):
    """Testet, ob SQL-Injection verhindert wird."""
    sql = "SELECT * FROM studiengang WHERE studiengangName = ?;"
    parameter = ("' OR 1=1; --",) # Angriffsversuch

    ergebnis = db_test.abfragen(sql, parameter)
    assert len(ergebnis) == 0, "SQL-Injection sollte nicht erfolgreich sein."

def test_view_erstellung(db_test):
    """Testet, ob Views korrekt erstellt werden."""
    db_test.initialisieren()
    
    sql = "SELECT name FROM sqlite_master WHERE type='view' AND name='startbildschirm';"
    ergebnis = db_test.abfragen(sql)
    assert len(ergebnis) == 1, "Die View 'startbildschirm' sollte existieren."