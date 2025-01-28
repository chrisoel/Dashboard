import logging
from datenbank_zugriff import DatenbankZugriff

class Logik:
    def __init__(self, db_pfad="data/datenbank.db"):
        self.logger = logging.getLogger("Logik")
        self.datenbank = DatenbankZugriff(db_pfad)
    
    def starten(self) -> bool:
        """Startet die Logik-Schicht und verbindet zur Datenbank."""
        try:
            self.logger.info("🚀 Logik-Schicht wird gestartet...")
            erfolgreich = self.datenbank.starten()
            if erfolgreich:
                self.logger.info("✅ Logik-Schicht erfolgreich gestartet.")
            else:
                self.logger.error("❌ Fehler beim Starten der Logik-Schicht.")
            return erfolgreich
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten der Logik-Schicht: {e}")
            return False
    
    def beenden(self) -> None:
        """Beendet die Logik-Schicht und trennt die Verbindung zur Datenbank."""
        self.logger.info("⏹️ Logik-Schicht wird beendet...")
        self.datenbank.trennen()
        self.logger.info("✅ Logik-Schicht erfolgreich beendet.")
    
    def get_daten(self, ansicht_name: str):
        """Holt Daten für eine bestimmte Ansicht."""
        sql = f"SELECT * FROM {ansicht_name};"
        try:
            self.logger.info(f"🔍 Abrufen von Daten für Ansicht '{ansicht_name}'...")
            ergebnisse = self.datenbank.abfragen(sql)
            self.logger.info(f"✅ Daten erfolgreich abgerufen: {ergebnisse}")
            return ergebnisse
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Abrufen von Daten für Ansicht '{ansicht_name}': {e}")
            return []
    
    def set_daten(self, tabelle: str, manipulation: str, daten: tuple) -> bool:
        """Fügt Daten in eine Tabelle ein oder aktualisiert sie."""
        self.logger.info(f"✏️ Verarbeitung einer '{manipulation.upper()}'-Operation für Tabelle '{tabelle}' mit Daten: {daten}")
        try:
            spalten = self.datenbank.abfragen(f"PRAGMA table_info({tabelle})")
            if not spalten:
                self.logger.error(f"❌ Tabelle '{tabelle}' existiert nicht.")
                return False

            spaltennamen = [spalte[1] for spalte in spalten]

            if manipulation.upper() == "INSERT":
                sql = f"INSERT INTO {tabelle} ({', '.join(spaltennamen)}) VALUES ({', '.join(['?' for _ in daten])});"
            elif manipulation.upper() == "UPDATE":
                spalten = ", ".join([f"{key} = ?" for key in daten.keys() if key != "id"])
                sql = f"UPDATE {tabelle} SET {spalten} WHERE modulID = ?;"
                parameter = tuple(daten.values()) + (daten["modulID"],)
            else:
                self.logger.error(f"❌ Ungültige Manipulationsart: '{manipulation}'")
                return False
            
            erfolgreich = self.datenbank.manipulieren(sql, daten)
            if erfolgreich:
                self.logger.info(f"✅ Manipulation erfolgreich: {manipulation} auf '{tabelle}'")
            else:
                self.logger.warning("⚠️ Manipulation war nicht erfolgreich (z. B. keine Zeilen betroffen).")
            return erfolgreich
        except Exception as e:
            self.logger.error(f"❌ Fehler bei der Manipulation: {e}")
            return False

    def get_startbildschirm_ansicht_daten(self):
        return self.get_daten("startbildschirm")
    
    def get_moduluebersicht_ansicht_daten(self):
        return self.get_daten("moduluebersicht")
    
    def get_studienfortschritt_ansicht_daten(self):
        return self.get_daten("studienfortschritt")
    
    def get_zeitmanagement_ansicht_daten(self):
        return self.get_daten("zeitmanagement")
    
    def get_einstellungen_ansicht_daten(self):
        return self.get_daten("einstellungen")
    
    def set_startbildschirm_ansicht_daten(self, daten: tuple):
        return self.set_daten("startbildschirm", "INSERT", daten)
    
    def set_moduluebersicht_ansicht_daten(self, daten: tuple):
        return self.set_daten("modul", "INSERT", daten)
    
    def set_studienfortschritt_ansicht_daten(self, daten: tuple):
        return self.set_daten("studienfortschritt", "INSERT", daten)
    
    def set_zeitmanagement_ansicht_daten(self, daten: tuple):
        return self.set_daten("zeitmanagement", "INSERT", daten)
    
    def set_einstellungen_ansicht_daten(self, daten: tuple):
        return self.set_daten("einstellungen", "INSERT", daten)