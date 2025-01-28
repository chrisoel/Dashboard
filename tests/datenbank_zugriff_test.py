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
    sql_insert = """
    INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    daten = ("Informatik", "2022-10-01", 0, "MO_DI_MI", "Vollzeit", 1)
    erfolg = db_test.manipulieren(sql_insert, daten)
    assert erfolg, "Das Einfügen von Daten sollte erfolgreich sein."

    sql_select = "SELECT studiengangName, startDatumStudium, urlaubsSemester FROM studiengang WHERE studiengangName = ?;"
    ergebnis = db_test.abfragen(sql_select, ("Informatik",))
    assert len(ergebnis) == 1, "Die Abfrage sollte genau einen Eintrag zurückgeben."
    assert ergebnis[0] == ("Informatik", "2022-10-01", 0), "Die abgefragten Daten stimmen nicht mit den eingefügten überein."


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


def test_view_erstellung(db_test):
    """Testet, ob Views korrekt erstellt werden."""
    db_test.initialisieren()
    
    sql = "SELECT name FROM sqlite_master WHERE type='view' AND name='startbildschirm';"
    ergebnis = db_test.abfragen(sql)
    assert len(ergebnis) == 1, "Die View 'startbildschirm' sollte existieren."


def test_datenbank_trennen_und_verbinden(db_test):
    """Testet, ob die Datenbank korrekt getrennt und wieder verbunden wird."""
    db_test.trennen()
    assert db_test.verbindung is None, "Die Verbindung sollte nach dem Trennen None sein."

    db_test.verbinden()
    assert db_test.verbindung is not None, "Die Verbindung sollte nach dem erneuten Verbinden nicht None sein."


def test_sql_injection_schutz(db_test):
    """Testet, ob SQL-Injection verhindert wird."""
    sql = "SELECT * FROM studiengang WHERE studiengangName = ?;"
    parameter = ("' OR 1=1; --",)  # Angriffsversuch
    ergebnis = db_test.abfragen(sql, parameter)
    assert len(ergebnis) == 0, "SQL-Injection sollte nicht erfolgreich sein."


def test_daten_aktualisieren(db_test):
    """Testet das Aktualisieren eines Datensatzes."""
    db_test.manipulieren(
        "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
        ("Medizintechnik", "2023-01-01", 0, "MO_DI", "Vollzeit", 42)
    )
    erfolg = db_test.manipulieren(
        "UPDATE studiengang SET arbeitstage = ? WHERE uniqueConstraint = ?;",
        ("MO_MI_DO", 42)
    )
    assert erfolg, "Das Update sollte erfolgreich sein."

    ergebnis = db_test.abfragen("SELECT arbeitstage FROM studiengang WHERE uniqueConstraint = ?;", (42,))
    assert ergebnis[0][0] == "MO_MI_DO", "Die Daten sollten erfolgreich aktualisiert worden sein."


def test_daten_loeschen(db_test):
    """Testet das Löschen eines Datensatzes."""
    db_test.manipulieren(
        "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
        ("Test-Studiengang", "2023-01-01", 0, "MO_MI", "Vollzeit", 99)
    )
    erfolg = db_test.manipulieren(
        "DELETE FROM studiengang WHERE uniqueConstraint = ?;",
        (99,)
    )
    assert erfolg, "Das Löschen sollte erfolgreich sein."

    ergebnis = db_test.abfragen("SELECT * FROM studiengang WHERE uniqueConstraint = ?;", (99,))
    assert len(ergebnis) == 0, "Der Datensatz sollte gelöscht worden sein."