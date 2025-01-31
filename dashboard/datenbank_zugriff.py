"""
@file datenbank_zugriff.py
@brief Klasse zur Verwaltung des Datenbankzugriffs.

Dieses Modul stellt Funktionen für den Zugriff auf eine SQLite-Datenbank bereit.
Es umfasst das Verbinden, Trennen, Initialisieren der Tabellen sowie CRUD-Operationen.

@author CHOE
@date 2025-01-31
@version 1.0
"""

import os
import sqlite3
import yaml
import logging
from pathlib import Path

class DatenbankZugriff:
    """
    @class DatenbankZugriff
    @brief Klasse für den Zugriff auf eine SQLite-Datenbank.
    """
    def __init__(self, db_pfad=None):
        """
        @brief Initialisiert die Datenbankverbindung.
        @param db_pfad Optionaler Pfad zur SQLite-Datenbank.
        """
        if db_pfad is None:
            base_path = Path(__file__).parent.parent / "data"
            self.db_pfad = str(base_path / "datenbank.db")
        else:
            self.db_pfad = db_pfad
        
        self.logger = logging.getLogger("DatenbankZugriff")
        self.verbindung = None

        db_verzeichnis = os.path.dirname(self.db_pfad)
        if not os.path.exists(db_verzeichnis):
            os.makedirs(db_verzeichnis, exist_ok=True)
            self.logger.info(f"📁 Verzeichnis '{db_verzeichnis}' wurde erfolgreich erstellt.")

    def starten(self) -> bool:
        """
        @brief Startet die Datenbankverbindung und initialisiert die Tabellen.
        @return True, wenn erfolgreich gestartet, sonst False.
        """
        try:
            self.logger.info("🚀 Datenbankzugriff wird gestartet...")
            self.verbinden()
            self.initialisieren()
            self.logger.info("✅ Datenbankzugriff erfolgreich gestartet.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Datenbankzugriffs: {e}")
            return False

    def verbinden(self):
        """
        @brief Verbindet mit der SQLite-Datenbank.
        """
        try:
            self.verbindung = sqlite3.connect(self.db_pfad)
            self.verbindung.execute("PRAGMA foreign_keys = ON;")
            self.logger.info(f"✅ Verbindung zur Datenbank '{self.db_pfad}' hergestellt.")
        except sqlite3.Error as e:
            self.logger.error(f"❌ Fehler beim Verbinden mit der Datenbank: {e}")
            raise

    def trennen(self):
        """
        @brief Schließt die Verbindung zur Datenbank.
        """
        if self.verbindung:
            self.verbindung.close()
            self.verbindung = None
            self.logger.info("✅ Datenbankverbindung erfolgreich geschlossen.")

    def initialisieren(self):
        """
        @brief Initialisiert Tabellen und Views basierend auf YAML-Definitionen.
        """
        yaml_verzeichnis = Path(__file__).parent.parent / "data"
        yaml_dateien = yaml_verzeichnis.glob("*.yaml")

        for yaml_datei in yaml_dateien:
            try:
                with open(yaml_datei, "r", encoding="utf-8") as file:
                    config = yaml.safe_load(file)
                    
                    if "tabelle" in config:
                        self._erstelle_tabelle(config)
                    
                    if "views" in config:
                        self._erstelle_views(config["views"])
                    
            except Exception as e:
                self.logger.error(f"❌ Fehler beim Initialisieren mit '{yaml_datei}': {e}")

    def _erstelle_views(self, views: dict):
        for view_name, view_sql_list in views.items():
            for view_sql in view_sql_list:
                try:
                    # Alle Zeilen, die mit '#' beginnen, raus filtern:
                    lines = []
                    for line in view_sql.split('\n'):
                        if not line.strip().startswith('#'):
                            lines.append(line)
                    cleaned_view_sql = "\n".join(lines)

                    cursor = self.verbindung.cursor()
                    cursor.execute(cleaned_view_sql)
                    self.logger.info(f"✅ View '{view_name}' erfolgreich erstellt.")
                except sqlite3.Error as e:
                    self.logger.error(f"❌ Fehler beim Erstellen der View '{view_name}': {e}")
                    raise

    def _erstelle_tabelle(self, model: dict):
        """
        @brief Erstellt Tabellen basierend auf YAML-Definitionen.
        @param model Dictionary mit Tabellenname und Spalten.
        """
        tabellen_name = model["tabelle"]
        spalten = model["spalten"]

        spalten_definitionen = []
        for spalte, definition in spalten.items():
            spalten_definitionen.append(f"{spalte} {definition}")

        sql_befehl = f"""
        CREATE TABLE IF NOT EXISTS {tabellen_name} (
            {', '.join(spalten_definitionen)}
        );
        """
        
        try:
            cursor = self.verbindung.cursor()
            cursor.execute(sql_befehl)
            self.verbindung.commit()
            self.logger.info(f"✅ Tabelle '{tabellen_name}' erfolgreich erstellt.")
        except sqlite3.Error as e:
            self.logger.error(f"❌ Fehler beim Erstellen der Tabelle '{tabellen_name}': {e}")
            raise

    def semester_vorbereiten(self, studiengang_id: int):
        """
        @brief Stellt sicher, dass die Semester 1 - 12 für den gegebenen Studiengang existieren.
        
        Diese Methode überprüft, ob für den angegebenen Studiengang bereits 12 Semester existieren.
        Falls weniger als 12 Semester vorhanden sind, werden die fehlenden Semester automatisch hinzugefügt.

        @param studiengang_id Die eindeutige ID des Studiengangs.
        """
        self.logger.info(f"📚 Überprüfe, ob Semester für Studiengang {studiengang_id} existieren...")

        # Anzahl der vorhandenen Semester abrufen
        vorhandene_semester = self.abfragen(
            "SELECT COUNT(*) FROM semester WHERE studiengangID = ?;",
            (studiengang_id,)
        )[0][0]

        # Falls weniger als 12 Semester existieren, fehlende Semester hinzufügen
        if vorhandene_semester < 12:
            self.logger.info(f"➕ Fehlen Semester für Studiengang {studiengang_id}, füge sie hinzu...")

            for semester_nr in range(1, 13):
                # Überprüfen, ob das Semester bereits existiert
                existiert = self.abfragen(
                    "SELECT semesterID FROM semester WHERE studiengangID = ? AND semesterNR = ?;",
                    (studiengang_id, semester_nr)
                )
                
                # Falls das Semester nicht existiert, hinzufügen
                if not existiert:
                    self.manipulieren(
                        "INSERT INTO semester (studiengangID, semesterNR, istUrlaubSemester) VALUES (?, ?, ?);",
                        (studiengang_id, semester_nr, 0)
                    )
                    self.logger.info(f"✅ Semester {semester_nr} für Studiengang {studiengang_id} hinzugefügt.")
        else:
            self.logger.info(f"✅ Alle Semester für Studiengang {studiengang_id} existieren bereits.")

    def abfragen(self, sql_befehl: str, parameter: tuple = ()) -> list:
        """
        @brief Führt eine SELECT-Abfrage aus und gibt die Ergebnisse zurück.
        @param sql_befehl Der auszuführende SQL-Befehl.
        @param parameter Optionale Parameter für die SQL-Abfrage.
        @return Liste der Abfrageergebnisse.
        """
        try:
            cursor = self.verbindung.cursor()
            cursor.execute(sql_befehl, parameter)
            ergebnisse = cursor.fetchall()
            self.logger.info(f"✅ Abfrage erfolgreich: {sql_befehl}")
            return ergebnisse
        except sqlite3.Error as e:
            self.logger.error(f"❌ Fehler bei der Abfrage: {e}")
            raise

    def manipulieren(self, sql_befehl: str, parameter: tuple = ()) -> bool:
        """
        @brief Führt eine Datenmanipulation (INSERT, UPDATE, DELETE) aus.
        @param sql_befehl Der auszuführende SQL-Befehl.
        @param parameter Optionale Parameter für die SQL-Abfrage.
        @return True, wenn erfolgreich, sonst False.
        """
        try:
            if not self.verbindung:
                self.logger.error("❌ Datenbankverbindung ist nicht aktiv.")
                return False
            cursor = self.verbindung.cursor()
            cursor.execute(sql_befehl, parameter)
            self.verbindung.commit()
            self.logger.info(f"✅ Manipulation erfolgreich: {sql_befehl}")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"❌ Fehler bei der Manipulation: {e}")
            return False

    def studiengang_speichern(self, studiengang_name: str, startdatum: str, urlaubssemester: int, zeitmodell: str) -> bool:
        """
        @brief Speichert einen neuen Studiengang in der Datenbank.

        Diese Methode speichert die Basisinformationen eines Studiengangs, einschließlich 
        Name, Startdatum, Urlaubssemester und Zeitmodell in der Tabelle `studiengang`. 
        Zusätzlich wird sichergestellt, dass die zugehörigen Semester erstellt werden.

        @param studiengang_name Der Name des Studiengangs.
        @param startdatum Das Startdatum des Studiengangs im Format 'YYYY-MM-DD'.
        @param urlaubssemester Die Anzahl der Urlaubssemester.
        @param zeitmodell Das Zeitmodell des Studiengangs (z.B. Vollzeit, Teilzeit).
        @return True, wenn der Studiengang erfolgreich gespeichert wurde, sonst False.
        """
        sql = """
        INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, zeitModell, uniqueConstraint)
        VALUES (?, ?, ?, ?, ?);
        """
        
        unique_constraint = 1  # Stellt sicher, dass nur ein Studiengang gespeichert wird
        daten = (studiengang_name, startdatum, urlaubssemester, zeitmodell, unique_constraint)

        self.logger.info(f"✏️ Speichern des Studiengangs: {daten}")
        erfolg = self.manipulieren(sql, daten)

        if erfolg:
            self.logger.info("✅ Studiengang erfolgreich gespeichert.")

            # Studiengang-ID abrufen, um die zugehörigen Semester vorzubereiten
            studiengang_id = self.abfragen(
                "SELECT studiengangID FROM studiengang WHERE uniqueConstraint = 1;"
            )[0][0]
            
            # Sicherstellen, dass die Semester für den Studiengang erstellt werden
            self.semester_vorbereiten(studiengang_id)

        return erfolg
    
    def modul_speichern(self, semester_id: int, modul_name: str, kuerzel: str, status: str, ects: int, startdatum: str) -> bool:
        """
        @brief Speichert ein neues Modul in der Datenbank.

        Diese Methode fügt ein neues Modul in die `modul`-Tabelle ein und ordnet es einem bestimmten Semester zu.
        Dabei werden Name, Kürzel, Status, ECTS-Punkte und das Startdatum des Moduls gespeichert.

        @param semester_id Die eindeutige ID des Semesters, dem das Modul zugeordnet wird.
        @param modul_name Der Name des Moduls.
        @param kuerzel Das Kürzel des Moduls (z. B. "INF101").
        @param status Der aktuelle Status des Moduls (z. B. "Offen", "In Bearbeitung", "Abgeschlossen").
        @param ects Die Anzahl der ECTS-Punkte für das Modul.
        @param startdatum Das Startdatum des Moduls im Format 'YYYY-MM-DD'.
        @return True, wenn das Modul erfolgreich gespeichert wurde, sonst False.
        """
        sql = """
        INSERT INTO modul (semesterID, modulName, modulKuerzel, modulStatus, modulEctsPunkte, modulStart)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        
        daten = (semester_id, modul_name, kuerzel, status, ects, startdatum)
        return self.manipulieren(sql, daten)
    
    def modul_aktualisieren(self, modul_id: int, modul_name: str, kuerzel: str, status: str, ects: int, startdatum: str) -> bool:
        """
        @brief Aktualisiert die Daten eines bestehenden Moduls in der Datenbank.

        Diese Methode aktualisiert den Namen, das Kürzel, den Status, die ECTS-Punkte und das Startdatum eines 
        vorhandenen Moduls in der `modul`-Tabelle anhand der Modul-ID.

        @param modul_id Die eindeutige ID des zu aktualisierenden Moduls.
        @param modul_name Der neue Name des Moduls.
        @param kuerzel Das neue Kürzel des Moduls (z. B. "INF101").
        @param status Der neue Status des Moduls (z. B. "Offen", "In Bearbeitung", "Abgeschlossen").
        @param ects Die neue Anzahl der ECTS-Punkte für das Modul.
        @param startdatum Das neue Startdatum des Moduls im Format 'YYYY-MM-DD'.
        @return True, wenn das Modul erfolgreich aktualisiert wurde, sonst False.
        """
        sql = """
        UPDATE modul
        SET modulName = ?, modulKuerzel = ?, modulStatus = ?, modulEctsPunkte = ?, modulStart = ?
        WHERE modulID = ?;
        """
        
        daten = (modul_name, kuerzel, status, ects, startdatum, modul_id)
        return self.manipulieren(sql, daten)
    
    def modul_loeschen(self, modul_id: int) -> bool:
        """
        @brief Löscht ein Modul aus der Datenbank.

        Diese Methode entfernt ein Modul aus der `modul`-Tabelle basierend auf der übergebenen Modul-ID.
        
        @param modul_id Die eindeutige ID des zu löschenden Moduls.
        @return True, wenn das Modul erfolgreich gelöscht wurde, sonst False.
        """
        sql = "DELETE FROM modul WHERE modulID = ?;"
        return self.manipulieren(sql, (modul_id,))
    
    def einstellungen_verwalten(self, aktion: str, daten: tuple = None) -> bool:
        """
        Verwaltet die Einstellungen der Datenbank (Aktualisieren oder Löschen).

        Aktionen:
        - "UPDATE": Aktualisiert die Studiengangsdaten
        - "DELETE": Löscht die gesamte Datenbank
        
        Parameter:
        - daten (tuple): (studiengangName, startDatumStudium, urlaubsSemester, zeitModell) für UPDATE
        """
        if aktion.upper() == "UPDATE":
            if not daten:
                self.logger.error("❌ Fehler: Keine Daten für das Update übergeben.")
                return False

            sql = """
            UPDATE studiengang 
            SET studiengangName = ?, startDatumStudium = ?, urlaubsSemester = ?, zeitModell = ?
            WHERE uniqueConstraint = 1;
            """
            self.logger.info(f"✏️ Aktualisiere Einstellungen: {daten}")
            return self.manipulieren(sql, daten)

        elif aktion.upper() == "DELETE":
            import os
            try:
                self.trennen()
                os.remove(self.db_pfad)
                self.logger.warning("⚠️ Datenbank erfolgreich gelöscht. Anwendung wird beendet.")
                return True
            except Exception as e:
                self.logger.error(f"❌ Fehler beim Löschen der Datenbank: {e}")
                return False

        else:
            self.logger.error(f"❌ Ungültige Aktion: {aktion}")
            return False
        
    def aktualisiere_studienfortschritt(self):
        """
        @brief Aktualisiert die Studienfortschrittsdaten in der Tabelle `verlauf`.

        Diese Methode überprüft den aktuellen Status der Module und aktualisiert 
        die Studienfortschrittsstatistik in der `verlauf`-Tabelle. Falls für das 
        aktuelle Datum noch kein Eintrag existiert, wird ein neuer Datensatz erstellt.

        @note Diese Methode zählt die Module in den verschiedenen Statuskategorien 
            ("Offen", "In Bearbeitung", "Abgeschlossen") und speichert die Ergebnisse 
            in der Datenbank.

        @exception sqlite3.Error Falls ein Fehler bei der Datenbankaktualisierung auftritt.
        """
        try:
            self.logger.info("🔄 Aktualisiere Studienfortschritt...")

            sql_update = """
            UPDATE verlauf
            SET 
                modulOffen = (SELECT COUNT(*) FROM modul WHERE modulStatus = 'Offen'),
                modulInBearbeitung = (SELECT COUNT(*) FROM modul WHERE modulStatus = 'In Bearbeitung'),
                modulAbgeschlossen = (SELECT COUNT(*) FROM modul WHERE modulStatus = 'Abgeschlossen')
            WHERE zeitpunkt = DATE('now');
            """
            cursor = self.verbindung.cursor()
            cursor.execute(sql_update)

            # Falls kein Eintrag für das heutige Datum existiert, neuen Eintrag erstellen
            if cursor.rowcount == 0:
                sql_insert = """
                INSERT INTO verlauf (modulOffen, modulInBearbeitung, modulAbgeschlossen, zeitpunkt)
                SELECT 
                    (SELECT COUNT(*) FROM modul WHERE modulStatus = 'Offen'),
                    (SELECT COUNT(*) FROM modul WHERE modulStatus = 'In Bearbeitung'),
                    (SELECT COUNT(*) FROM modul WHERE modulStatus = 'Abgeschlossen'),
                    DATE('now')
                WHERE NOT EXISTS (SELECT 1 FROM verlauf WHERE zeitpunkt = DATE('now'));
                """
                cursor.execute(sql_insert)

            self.verbindung.commit()
            self.logger.info("✅ Studienfortschritt erfolgreich aktualisiert.")
        
        except sqlite3.Error as e:
            self.logger.error(f"❌ Fehler beim Aktualisieren des Studienfortschritts: {e}")