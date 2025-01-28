import logging
from dashboard.datenbank_zugriff import DatenbankZugriff

class Logik:
    def __init__(self, db_pfad="data/datenbank.db"):
        self.logger = logging.getLogger("Logik")
        self.datenbank = DatenbankZugriff(db_pfad)
    
    def starten(self) -> bool:
        """Startet die Logik-Schicht und verbindet zur Datenbank."""
        try:
            self.logger.info("Logik-Schicht wird gestartet...")
            return self.datenbank.starten()
        except Exception as e:
            self.logger.error(f"Fehler beim Starten der Logik-Schicht: {e}")
            return False
    
    def beenden(self) -> None:
        """Beendet die Logik-Schicht und trennt die Verbindung zur Datenbank."""
        self.logger.info("Logik-Schicht wird beendet...")
        self.datenbank.trennen()
    
    def get_daten(self, ansicht_name: str):
        """Holt Daten für eine bestimmte Ansicht."""
        sql = f"SELECT * FROM {ansicht_name};"
        try:
            return self.datenbank.abfragen(sql)
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen von Daten für Ansicht '{ansicht_name}': {e}")
            return []
    
    def set_daten(self, tabelle: str, manipulation: str, daten: tuple) -> bool:
        """Fügt Daten in eine Tabelle ein oder aktualisiert sie."""
        if manipulation.upper() == "INSERT":
            # INSERT-Statement generieren
            sql = f"INSERT INTO {tabelle} VALUES ({', '.join(['?' for _ in daten])});"
        elif manipulation.upper() == "UPDATE":
            # UPDATE-Statement generieren (spalten und where)
            spalten = ", ".join([f"{col} = ?" for col in ["name"]])  # Spaltennamen explizit angeben
            sql = f"UPDATE {tabelle} SET {spalten} WHERE id = ?;"
            daten = daten[1:] + daten[:1]  # Reihenfolge der Daten für das WHERE anpassen
        else:
            self.logger.error(f"Ungültige Manipulation: {manipulation}")
            return False

        return self.datenbank.manipulieren(sql, daten)
    
    # Methoden für spezifische Ansichten
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
    
    # Methoden zum Speichern von spezifischen Ansichten
    def set_startbildschirm_ansicht_daten(self, daten: tuple):
        return self.set_daten("startbildschirm", "INSERT", daten)
    
    def set_moduluebersicht_ansicht_daten(self, daten: tuple):
        return self.set_daten("moduluebersicht", "INSERT", daten)
    
    def set_studienfortschritt_ansicht_daten(self, daten: tuple):
        return self.set_daten("studienfortschritt", "INSERT", daten)
    
    def set_zeitmanagement_ansicht_daten(self, daten: tuple):
        return self.set_daten("zeitmanagement", "INSERT", daten)
    
    def set_einstellungen_ansicht_daten(self, daten: tuple):
        return self.set_daten("einstellungen", "INSERT", daten)    
    
if __name__ == "__main__":
    logik = Logik()
    if logik.starten():
        print("Logik-Schicht erfolgreich gestartet.")
        logik.beenden()