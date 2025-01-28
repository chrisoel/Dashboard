import pytest
from dashboard.logik import Logik
from dashboard.datenbank_zugriff import DatenbankZugriff
from pathlib import Path

@pytest.fixture(scope="function")
def logik_test():
    """Fixture zum Erstellen einer frischen Logik-Instanz für jeden Test."""
    test_db_pfad = "data/test_datenbank.db"
    
    # Entferne die alte Test-Datenbank, falls vorhanden
    if Path(test_db_pfad).exists():
        Path(test_db_pfad).unlink()
    
    # Erstelle eine neue Instanz der Logik-Schicht
    logik = Logik(db_pfad=test_db_pfad)
    logik.starten()
    yield logik  # Logik-Instanz für den Test bereitstellen
    
    # Test-Datenbank löschen
    logik.beenden()
    if Path(test_db_pfad).exists():
        Path(test_db_pfad).unlink()


def test_logik_verbindung(logik_test):
    """Testet, ob die Logik-Schicht erfolgreich gestartet wird."""
    assert logik_test.datenbank.verbindung is not None, "Die Verbindung zur Datenbank sollte bestehen."


def test_get_daten(logik_test):
    """Testet, ob Daten aus einer Tabelle abgefragt werden können."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)
    logik_test.datenbank.manipulieren("INSERT INTO test_tabelle (name) VALUES (?);", ("Test-Eintrag",))
    
    ergebnis = logik_test.get_daten("test_tabelle")
    assert len(ergebnis) == 1, "Die Abfrage sollte einen Eintrag zurückgeben."
    assert ergebnis[0][1] == "Test-Eintrag", "Der Wert des ersten Eintrags sollte 'Test-Eintrag' sein."


def test_set_daten(logik_test):
    """Testet, ob Daten erfolgreich in die Datenbank eingefügt werden."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)
    
    erfolg = logik_test.set_daten("test_tabelle", "INSERT", (1, "Neuer Eintrag"))
    assert erfolg, "Das Einfügen sollte erfolgreich sein."
    
    ergebnis = logik_test.get_daten("test_tabelle")
    assert len(ergebnis) == 1, "Es sollte genau ein Eintrag vorhanden sein."
    assert ergebnis[0][1] == "Neuer Eintrag", "Der Wert des ersten Eintrags sollte 'Neuer Eintrag' sein."


def test_get_moduluebersicht_ansicht_daten(logik_test):
    """Testet, ob die Modulübersicht korrekt abgefragt werden kann."""
    logik_test.datenbank.initialisieren()

    logik_test.datenbank.manipulieren(
        """
        INSERT INTO semester (studiengangID, semesterNR, istUrlaubSemester)
        VALUES (?, ?, ?);
        """,
        (1, 1, 0)
    )

    logik_test.datenbank.manipulieren(
        """
        INSERT INTO modul (semesterID, modulName, modulKuerzel, modulStatus, modulPruefungsform, modulNote, modulEctsPunkte, modulStart)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (1, "Softwareentwicklung", "SE1", "Offen", "Klausur", None, 5, "2023-10-01")
    )

    ergebnis = logik_test.get_moduluebersicht_ansicht_daten()
    assert len(ergebnis) == 1, "Es sollte genau ein Modul-Eintrag vorhanden sein."
    assert ergebnis[0][0] == "Softwareentwicklung", "Der Modulname sollte 'Softwareentwicklung' sein."

def test_get_daten_invalid(logik_test):
    """Testet, ob eine nicht existierende Tabelle abgefragt werden kann (sollte fehlschlagen)."""
    ergebnis = logik_test.get_daten("nicht_existierende_tabelle")
    assert isinstance(ergebnis, list), "Ergebnis sollte eine Liste sein"
    assert len(ergebnis) == 0, "Die Abfrage einer nicht existierenden Tabelle sollte eine leere Liste zurückgeben."

def test_set_daten_invalid(logik_test):
    """Testet, ob das Einfügen in eine nicht existierende Tabelle fehlschlägt."""
    erfolg = logik_test.set_daten("nicht_existierende_tabelle", "INSERT", (1, "Testwert"))
    assert not erfolg, "Das Einfügen in eine nicht existierende Tabelle sollte fehlschlagen."

def test_set_daten_empty(logik_test):
    """Testet, ob das Einfügen leerer Daten fehlschlägt."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT NOT NULL);"
    logik_test.datenbank.manipulieren(sql_create)
    
    erfolg = logik_test.set_daten("test_tabelle", "INSERT", (1, None))
    assert not erfolg, "Das Einfügen leerer Daten sollte fehlschlagen."

def test_update_daten(logik_test):
    """Testet das Aktualisieren von Daten in einer Tabelle."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)
    logik_test.set_daten("test_tabelle", "INSERT", (1, "Alter Name"))

    erfolg = logik_test.set_daten("test_tabelle", "UPDATE", (1, "Neuer Name"))
    assert erfolg, "Das Update sollte erfolgreich sein."

    ergebnis = logik_test.get_daten("test_tabelle")
    assert ergebnis[0][1] == "Neuer Name", "Der Name sollte aktualisiert worden sein."

def test_get_empty_table(logik_test):
    """Testet, ob eine leere Tabelle korrekt abgefragt wird."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)

    ergebnis = logik_test.get_daten("test_tabelle")
    assert isinstance(ergebnis, list), "Ergebnis sollte eine Liste sein."
    assert len(ergebnis) == 0, "Die Liste sollte leer sein, da die Tabelle keine Einträge enthält."

def test_invalid_manipulation(logik_test):
    """Testet, ob eine ungültige Manipulation korrekt behandelt wird."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)

    erfolg = logik_test.set_daten("test_tabelle", "DELETE", (1, "Ungültig"))
    assert not erfolg, "Eine ungültige Manipulation sollte fehlschlagen."

def test_disconnect_during_operation(logik_test):
    """Testet, ob die Logik korrekt mit einer getrennten Datenbankverbindung umgeht."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)

    logik_test.datenbank.trennen()

    erfolg = logik_test.set_daten("test_tabelle", "INSERT", (1, "Getrennte Verbindung"))
    assert not erfolg, "Operationen ohne aktive Verbindung sollten fehlschlagen."

def test_table_without_primary_key(logik_test):
    """Testet, ob eine Tabelle ohne Primärschlüssel korrekt genutzt werden kann."""
    sql_create = "CREATE TABLE test_tabelle (name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)

    erfolg = logik_test.set_daten("test_tabelle", "INSERT", ("Kein Primärschlüssel",))
    assert erfolg, "Das Einfügen sollte auch ohne Primärschlüssel funktionieren."

def test_error_logging(logik_test, caplog):
    """Testet, ob ein Fehler korrekt im Logger protokolliert wird."""
    ergebnis = logik_test.get_daten("nicht_existierende_tabelle")

    assert len(ergebnis) == 0, "Die Abfrage sollte eine leere Liste zurückgeben."
    assert "Fehler beim Abrufen von Daten" in caplog.text, "Der Fehler sollte im Logger erscheinen."

def test_update_nonexistent_row(logik_test):
    """Testet, ob ein Update auf eine nicht existierende Zeile korrekt fehlschlägt."""
    sql_create = "CREATE TABLE test_tabelle (id INTEGER PRIMARY KEY, name TEXT);"
    logik_test.datenbank.manipulieren(sql_create)

    erfolg = logik_test.set_daten("test_tabelle", "UPDATE", (1, "Nicht vorhanden"))
    assert not erfolg, "Das Update sollte fehlschlagen, da die Zeile nicht existiert."

def test_view_abfrage(logik_test):
    """Testet, ob Daten aus der View korrekt abgefragt werden können."""
    logik_test.datenbank.manipulieren(
        "INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint) VALUES (?, ?, ?, ?, ?, ?);",
        ("Informatik", "2022-10-01", 0, "MO_DI", "Vollzeit", 1)
    )
    ergebnis = logik_test.get_startbildschirm_ansicht_daten()
    assert len(ergebnis) == 1, "Die View-Abfrage sollte einen Eintrag zurückgeben."
    assert ergebnis[0][0] == "Informatik", "Der erste Eintrag sollte 'Informatik' sein."