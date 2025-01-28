import sqlite3
import yaml
import logging
from pathlib import Path

class DatenbankZugriff:
    def __init__(self, db_pfad="data/datenbank.db"):
        self.db_pfad = db_pfad
        self.logger = logging.getLogger("DatenbankZugriff")
        self.verbindung = None

    def starten(self) -> bool:
        try:
            self.logger.info("Datenbankzugriff wird gestartet...")
            self.verbinden()
            self.initialisieren()
            self.logger.info("Datenbankzugriff erfolgreich gestartet.")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Starten des Datenbankzugriffs: {e}")
            return False

    def verbinden(self):
        try:
            self.verbindung = sqlite3.connect(self.db_pfad)
            self.verbindung.execute("PRAGMA foreign_keys = ON;")
            self.logger.info(f"Verbindung zur Datenbank '{self.db_pfad}' hergestellt.")
        except sqlite3.Error as e:
            self.logger.error(f"Fehler beim Verbinden mit der Datenbank: {e}")
            raise

    def trennen(self):
        if self.verbindung:
            self.verbindung.close()
            self.verbindung = None
            self.logger.info("Datenbankverbindung geschlossen.")

    def initialisieren(self):
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
                self.logger.error(f"Fehler beim Initialisieren mit '{yaml_datei}': {e}")

    def _erstelle_views(self, views: dict):
        """Erstellt SQL-Views basierend auf den YAML-Definitionen."""
        for view_name, view_sql_list in views.items():
            for view_sql in view_sql_list:
                try:
                    cursor = self.verbindung.cursor()
                    cursor.execute(view_sql)
                    self.logger.info(f"View '{view_name}' erfolgreich erstellt.")
                except sqlite3.Error as e:
                    self.logger.error(f"Fehler beim Erstellen der View '{view_name}': {e}")
                    raise

    def _erstelle_tabelle(self, model: dict):
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
        except sqlite3.Error as e:
            self.logger.error(f"Fehler beim Erstellen der Tabelle '{tabellen_name}': {e}")
            raise

    def abfragen(self, sql_befehl: str, parameter: tuple = ()) -> list:
        try:
            cursor = self.verbindung.cursor()
            cursor.execute(sql_befehl, parameter)
            ergebnisse = cursor.fetchall()
            return ergebnisse
        except sqlite3.Error as e:
            self.logger.error(f"Fehler bei der Abfrage: {e}")
            raise

    def manipulieren(self, sql_befehl: str, parameter: tuple = ()) -> bool:
        try:
            if not self.verbindung:
                self.logger.error("Datenbankverbindung ist nicht aktiv.")
                return False
            cursor = self.verbindung.cursor()
            cursor.execute(sql_befehl, parameter)
            self.verbindung.commit()
            if cursor.rowcount == 0:
                self.logger.warning("Keine Zeilen betroffen.")
                return False
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Fehler bei der Manipulation: {e}")
            return False