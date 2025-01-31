import logging
from datenbank_zugriff import DatenbankZugriff

class Logik:
    def __init__(self, db_pfad="data/datenbank.db"):
        self.logger = logging.getLogger("Logik")
        self.datenbank = DatenbankZugriff(db_pfad)
    
    def starten(self) -> bool:
        """Startet die Logik-Schicht und verbindet zur Datenbank."""
        self.logger.info("🚀 Starte Logik-Schicht...")
        try:
            erfolgreich = self.datenbank.starten()
            if erfolgreich:
                self.logger.info("✅ Logik-Schicht erfolgreich gestartet.")
            else:
                self.logger.error("❌ Fehler beim Start der Logik-Schicht.")
            return erfolgreich
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten: {e}")
            return False
    
    def beenden(self) -> None:
        """Beendet die Logik-Schicht und trennt die Verbindung zur Datenbank."""
        self.logger.info("⏹️ Beende Logik-Schicht...")
        self.datenbank.trennen()
        self.logger.info("✅ Logik-Schicht erfolgreich beendet.")
    
    def get_daten_ansicht(self, ansicht_name: str):
        """Holt Daten für eine bestimmte Ansicht."""
        sql = f"SELECT * FROM {ansicht_name};"
        try:
            self.logger.info(f"🔍 Abrufe Daten für Ansicht '{ansicht_name}'...")
            ergebnisse = self.datenbank.abfragen(sql)
            self.logger.info(f"✅ Daten erfolgreich geladen: {len(ergebnisse)} Einträge.")
            return ergebnisse
        except Exception as e:
            self.logger.error(f"❌ Fehler bei '{ansicht_name}': {e}")
            return []
    
    def manipuliere_daten(self, tabelle: str, aktion: str, daten: tuple) -> bool:
        """Führt eine Datenmanipulation (INSERT, UPDATE, DELETE) aus."""
        try:
            self.logger.info(f"✏️ Verarbeitung einer '{aktion.upper()}'-Operation für '{tabelle}' mit Daten: {daten}")

            if aktion.upper() == "INSERT":
                erfolgreich = self.datenbank.manipulieren(
                    f"INSERT INTO {tabelle} VALUES ({', '.join(['?' for _ in daten])});", daten
                )
            elif aktion.upper() == "UPDATE":
                spalten = self.datenbank.abfragen(f"PRAGMA table_info({tabelle})")
                if not spalten:
                    self.logger.error(f"❌ Tabelle '{tabelle}' existiert nicht.")
                    return False

                spaltennamen = [spalte[1] for spalte in spalten if spalte[1] != "id"]
                sql = f"UPDATE {tabelle} SET {', '.join([f'{spalte} = ?' for spalte in spaltennamen])} WHERE id = ?;"
                erfolgreich = self.datenbank.manipulieren(sql, daten)

            elif aktion.upper() == "DELETE":
                erfolgreich = self.datenbank.manipulieren(f"DELETE FROM {tabelle} WHERE id = ?;", (daten[0],))

            else:
                self.logger.error(f"❌ Ungültige Aktion '{aktion}' für '{tabelle}'")
                return False

            if erfolgreich:
                self.logger.info(f"✅ {aktion} erfolgreich für '{tabelle}'")
            else:
                self.logger.warning(f"⚠️ {aktion} nicht erfolgreich (keine Zeilen betroffen).")
            return erfolgreich

        except Exception as e:
            self.logger.error(f"❌ Fehler bei '{aktion}' in '{tabelle}': {e}")
            return False

    def get_startbildschirm_ansicht_daten(self):
        return self.get_daten_ansicht("startbildschirm")
    
    def get_moduluebersicht_ansicht_daten(self):
        return self.get_daten_ansicht("moduluebersicht")
    
    def get_studienfortschritt_ansicht_daten(self):
        return self.get_daten_ansicht("studienfortschritt")
    
    def get_zeitmanagement_ansicht_daten(self):
        return self.get_daten_ansicht("zeitmanagement")
    
    def get_einstellungen_ansicht_daten(self):
        return self.get_daten_ansicht("einstellungen")
    
    def set_startbildschirm_ansicht_daten(self, daten: tuple) -> bool:
        """Speichert die Studiengangsdaten ohne Arbeitstage."""
        if len(daten) != 4:
            self.logger.error("❌ Ungültige Anzahl an Parametern für den Studiengang.")
            return False

        self.logger.info(f"✏️ Speichern des Studiengangs: {daten}")
        return self.datenbank.studiengang_speichern(*daten)
    
    def set_moduluebersicht_ansicht_daten(self, aktion: str, daten: tuple) -> bool:
        """Bearbeitet Moduleinträge (INSERT, UPDATE, DELETE)."""
        try:
            if aktion.upper() == "INSERT":
                self.logger.info(f"➕ Neues Modul wird eingefügt: {daten}")
                erfolg = self.datenbank.modul_speichern(*daten)

            elif aktion.upper() == "UPDATE":
                self.logger.info(f"✏️ Modul wird aktualisiert: {daten}")
                erfolg = self.datenbank.modul_aktualisieren(*daten)

            elif aktion.upper() == "DELETE":
                self.logger.info(f"🗑️ Modul wird gelöscht: ID {daten[0]}")
                erfolg = self.datenbank.modul_loeschen(daten[0])

            else:
                self.logger.error(f"❌ Ungültige Aktion '{aktion}' für Modulbearbeitung.")
                return False

            if erfolg:
                self.logger.info(f"✅ Aktion '{aktion}' erfolgreich durchgeführt.")
            else:
                self.logger.warning(f"⚠️ Aktion '{aktion}' war nicht erfolgreich.")

            return erfolg

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Modulbearbeitung ({aktion}): {e}")
            return False

    def pruefe_semester_id(self) -> int:
        """Holt die aktuelle Semester-ID (falls keine vorhanden, wird 1 genutzt)."""
        ergebnis = self.datenbank.abfragen("SELECT semesterID FROM semester ORDER BY semesterID DESC LIMIT 1;")
        return ergebnis[0][0] if ergebnis else 1
    
    def set_studienfortschritt_ansicht_daten(self, daten: tuple):
        return self.manipuliere_daten("studienfortschritt", "INSERT", daten)
    
    def set_zeitmanagement_ansicht_daten(self, daten: tuple):
        return self.manipuliere_daten("zeitmanagement", "INSERT", daten)
    
    def set_einstellungen_ansicht_daten(self, aktion: str, daten: tuple = None) -> bool:
        """Setzt oder löscht die Einstellungen in der Datenbank."""
        return self.datenbank.einstellungen_verwalten(aktion, daten)