import os
import sqlite3
import yaml
import logging
from pathlib import Path

class DatenbankZugriff:
    def __init__(self, db_pfad="data/datenbank.db"):
        self.db_pfad = db_pfad
        self.logger = logging.getLogger("DatenbankZugriff")
        self.verbindung = None

        db_verzeichnis = os.path.dirname(self.db_pfad)
        if not os.path.exists(db_verzeichnis):
            os.makedirs(db_verzeichnis, exist_ok=True)
            self.logger.info(f"📁 Verzeichnis '{db_verzeichnis}' wurde erfolgreich erstellt.")

    def starten(self) -> bool:
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
        """Verbindet mit der Datenbank und aktiviert Foreign Keys."""
        try:
            self.verbindung = sqlite3.connect(self.db_pfad)
            self.verbindung.execute("PRAGMA foreign_keys = ON;")
            self.logger.info(f"✅ Verbindung zur Datenbank '{self.db_pfad}' hergestellt.")
        except sqlite3.Error as e:
            self.logger.error(f"❌ Fehler beim Verbinden mit der Datenbank: {e}")
            raise

    def trennen(self):
        """Schließt die Datenbankverbindung."""
        if self.verbindung:
            self.verbindung.close()
            self.verbindung = None
            self.logger.info("✅ Datenbankverbindung erfolgreich geschlossen.")

    def initialisieren(self):
        """Initialisiert Tabellen und Views basierend auf den YAML-Dateien."""
        yaml_verzeichnis = Path("data")
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
        """Erstellt SQL-Views basierend auf den YAML-Definitionen."""
        for view_name, view_sql_list in views.items():
            for view_sql in view_sql_list:
                try:
                    cursor = self.verbindung.cursor()
                    cursor.execute(view_sql)
                    self.logger.info(f"✅ View '{view_name}' erfolgreich erstellt.")
                except sqlite3.Error as e:
                    self.logger.error(f"❌ Fehler beim Erstellen der View '{view_name}': {e}")
                    raise

    def _erstelle_tabelle(self, model: dict):
        """Erstellt Tabellen basierend auf den YAML-Definitionen."""
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

    def abfragen(self, sql_befehl: str, parameter: tuple = ()) -> list:
        """Führt eine SELECT-Abfrage aus und gibt die Ergebnisse zurück."""
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
        """Führt eine INSERT, UPDATE oder DELETE-Operation aus."""
        try:
            if not self.verbindung:
                self.logger.error("❌ Datenbankverbindung ist nicht aktiv.")
                return False
            cursor = self.verbindung.cursor()
            cursor.execute(sql_befehl, parameter)
            self.verbindung.commit()
            if cursor.rowcount == 0:
                self.logger.warning("⚠️ Keine Zeilen betroffen.")
                return False
            self.logger.info(f"✅ Manipulation erfolgreich: {sql_befehl}")

            self.aktualisiere_studienfortschritt()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"❌ Fehler bei der Manipulation: {e}")
            return False

    def studiengang_speichern(self, studiengang_name: str, startdatum: str, urlaubssemester: int, arbeitstage: str, zeitmodell: str) -> bool:
        """
        Speichert den Studiengang und das Startdatum in der 'studiengang'-Tabelle.
        """
        sql = """
        INSERT INTO studiengang (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell, uniqueConstraint)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        unique_constraint = 1
        daten = (studiengang_name, startdatum, urlaubssemester, arbeitstage, zeitmodell, unique_constraint)

        self.logger.info(f"✏️ Speichern des Studiengangs: {daten}")
        return self.manipulieren(sql, daten)
    
    def modul_speichern(
        self,
        semester_nr: int,
        modul_name: str,
        modul_kuerzel: str,
        modul_status: str = "Offen",
        modul_pruefungsform: str = "Klausur",
        modul_note: float = None,
        modul_ects: int = 5,
        modul_start: str = None
    ) -> bool:
        """
        Speichert ein Modul in der 'modul'-Tabelle.
        Falls das angegebene Semester nicht existiert, wird es automatisch angelegt.
        """

        self.logger.info(f"✏️ Versuche, Modul zu speichern: {modul_name}, {modul_kuerzel} für Semester {semester_nr}")

        semester = self.abfragen(
            "SELECT semesterID FROM semester WHERE semesterNR = ? ORDER BY semesterID DESC LIMIT 1;",
            (semester_nr,)
        )

        if not semester:
            self.logger.warning(f"⚠️ Semester {semester_nr} existiert nicht. Erstelle neues Semester...")
            self.manipulieren(
                "INSERT INTO semester (studiengangID, semesterNR, istUrlaubSemester) VALUES (?, ?, ?);",
                (1, semester_nr, 0)
            )
            semester = self.abfragen(
                "SELECT semesterID FROM semester WHERE semesterNR = ? ORDER BY semesterID DESC LIMIT 1;",
                (semester_nr,)
            )

        semester_id = semester[0][0]
        self.logger.info(f"📚 Verwende semesterID = {semester_id} für Modul {modul_name}.")

        sql = """
        INSERT INTO modul (semesterID, modulName, modulKuerzel, modulStatus, modulPruefungsform, modulNote, modulEctsPunkte, modulStart)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """

        daten = (semester_id, modul_name, modul_kuerzel, modul_status, modul_pruefungsform, modul_note, modul_ects, modul_start)

        erfolg = self.manipulieren(sql, daten)

        if erfolg:
            self.logger.info(f"✅ Modul erfolgreich gespeichert: {daten}")
        else:
            self.logger.error(f"❌ Fehler beim Speichern des Moduls: {daten}")

        return erfolg
    
    def modul_aktualisieren(self, modul_id: int, modulname: str, kuerzel: str, status: str, pruefungsform: str, note, ects: int, startdatum: str) -> bool:
        """
        Aktualisiert die Daten eines Moduls basierend auf der modulID.
        """
        self.logger.info(f"✏️ Aktualisiere Modul mit ID {modul_id}...")

        vorhandene_eintraege = self.abfragen("SELECT modulID FROM modul WHERE modulID = ?;", (modul_id,))
        if not vorhandene_eintraege:
            self.logger.error(f"❌ Fehler: Modul mit ID {modul_id} existiert nicht.")
            return False

        sql = """
        UPDATE modul
        SET modulName = ?, modulKuerzel = ?, modulStatus = ?, modulPruefungsform = ?, modulNote = ?, modulEctsPunkte = ?, modulStart = ?
        WHERE modulID = ?;
        """
        daten = (modulname, kuerzel, status, pruefungsform, note, ects, startdatum, modul_id)

        erfolg = self.manipulieren(sql, daten)

        if erfolg:
            self.logger.info(f"✅ Modul erfolgreich aktualisiert: ID {modul_id}")
        else:
            self.logger.warning(f"⚠️ Modul konnte nicht aktualisiert werden: ID {modul_id}")
        
        return erfolg
    
    def modul_loeschen(self, modul_id: int) -> bool:
            """
            Löscht ein Modul aus der Datenbank basierend auf der modulID.
            """
            self.logger.info(f"🗑️ Lösche Modul mit ID {modul_id}...")

            vorhandene_eintraege = self.abfragen("SELECT modulID FROM modul WHERE modulID = ?;", (modul_id,))
            if not vorhandene_eintraege:
                self.logger.error(f"❌ Fehler: Modul mit ID {modul_id} existiert nicht und kann nicht gelöscht werden.")
                return False

            sql = "DELETE FROM modul WHERE modulID = ?;"
            erfolg = self.manipulieren(sql, (modul_id,))

            if erfolg:
                self.logger.info(f"✅ Modul erfolgreich gelöscht: ID {modul_id}")
            else:
                self.logger.warning(f"⚠️ Modul konnte nicht gelöscht werden: ID {modul_id}")

            return erfolg
    
    def einstellungen_verwalten(self, aktion: str, daten: tuple = None) -> bool:
        """
        Verwaltet die Einstellungen der Datenbank (Aktualisieren oder Löschen).

        Aktionen:
        - "UPDATE": Aktualisiert die Studiengangsdaten
        - "DELETE": Löscht die gesamte Datenbank
        
        Parameter:
        - daten (tuple): (studiengangName, startDatumStudium, urlaubsSemester, arbeitstage, zeitModell) für UPDATE
        """
        if aktion.upper() == "UPDATE":
            if not daten:
                self.logger.error("❌ Fehler: Keine Daten für das Update übergeben.")
                return False

            sql = """
            UPDATE studiengang 
            SET studiengangName = ?, startDatumStudium = ?, urlaubsSemester = ?, arbeitstage = ?, zeitModell = ?
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
        """Aktualisiert die Studienfortschrittsdaten in der Tabelle 'verlauf'."""
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