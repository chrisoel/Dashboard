"""
@file logik.py
@brief Zentrale Logik-Schicht der Anwendung.

Dieses Modul stellt die Kernlogik der Anwendung bereit und verwaltet 
den Zugriff auf die Datenbank. Es steuert die Interaktion zwischen der 
Datenbank und der GUI.

Es enthält Methoden zur Verwaltung von Studiengängen, Modulen, Studienfortschritt, 
Zeitmanagement und Einstellungen.

@author CHOE
@date 2025-01-31
@version 1.0
"""

import logging
from datenbank_zugriff import DatenbankZugriff

class Logik:
    """
    @class Logik
    @brief Enthält die zentrale Geschäftslogik der Anwendung.

    Diese Klasse verwaltet die Kommunikation zwischen der grafischen Oberfläche 
    und der Datenbank. Sie bietet Methoden zur Steuerung der Datenbankzugriffe 
    und zur Durchführung von CRUD-Operationen.
    """

    def __init__(self, db_pfad=None):
        """
        @brief Initialisiert die Logik-Schicht.

        Erstellt eine Verbindung zur Datenbank und setzt das Logging für die Logik-Klasse auf.
        db_pfad (optional): Über diesen Pfad wird die Test-DB angegeben.
        """
        self.logger = logging.getLogger("Logik")
        self.datenbank = DatenbankZugriff(db_pfad=db_pfad)
        
    def starten(self) -> bool:
        """
        @brief Startet die Logik-Schicht und verbindet zur Datenbank.

        Diese Methode initialisiert die Logik-Schicht und stellt sicher, 
        dass die Verbindung zur Datenbank hergestellt wird.

        @return True, wenn der Start erfolgreich war, sonst False.
        """
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
        """
        @brief Beendet die Logik-Schicht und trennt die Verbindung zur Datenbank.

        Diese Methode sorgt dafür, dass die Verbindung zur Datenbank sicher geschlossen wird.
        """
        self.logger.info("⏹️ Beende Logik-Schicht...")
        self.datenbank.trennen()
        self.logger.info("✅ Logik-Schicht erfolgreich beendet.")
    
    def get_daten_ansicht(self, ansicht_name: str):
        """
        @brief Ruft Daten für eine bestimmte Ansicht aus der Datenbank ab.

        @param ansicht_name Name der Datenbanktabelle, aus der Daten geladen werden sollen.
        @return Eine Liste mit den Ergebnissen der SQL-Abfrage oder eine leere Liste bei Fehlern.
        """
        sql = f"SELECT * FROM {ansicht_name};"
        try:
            self.logger.info(f"🔍 Abrufe Daten für Ansicht '{ansicht_name}'...")
            ergebnisse = self.datenbank.abfragen(sql)
            self.logger.info(f"✅ Daten erfolgreich geladen: {len(ergebnisse)} Einträge.")
            return ergebnisse
        except Exception as e:
            self.logger.error(f"❌ Fehler bei '{ansicht_name}': {e}")
            return []
    
    def get_moduluebersicht_ansicht_daten(self):
        """
        @brief Ruft die Daten für die Modulübersicht aus der Datenbank ab.

        @return Eine Liste mit den Moduldaten.
        """
        return self.get_daten_ansicht("moduluebersicht")

    def set_moduluebersicht_ansicht_daten(self, aktion: str, daten: tuple) -> bool:
        """
        @brief Bearbeitet Moduleinträge (INSERT, UPDATE, DELETE).

        @param aktion Die gewünschte Aktion ("INSERT", "UPDATE", "DELETE").
        @param daten Ein Tupel mit den erforderlichen Daten für die Aktion.
        @return True, wenn die Aktion erfolgreich war, sonst False.
        """
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

    def get_startbildschirm_ansicht_daten(self):
        """
        @brief Ruft die Daten für den Startbildschirm aus der Datenbank ab.

        @return Eine Liste mit den Startbildschirm-Daten.
        """
        return self.get_daten_ansicht("startbildschirm")
    
    def set_startbildschirm_ansicht_daten(self, daten: tuple) -> bool:
        """
        @brief Speichert die Studiengangsdaten in der Datenbank.

        @param daten Ein Tupel mit (Studiengangsname, Startdatum, Urlaubssemester, Zeitmodell).
        @return True, wenn das Speichern erfolgreich war, sonst False.
        """
        if len(daten) != 4:
            self.logger.error("❌ Ungültige Anzahl an Parametern für den Studiengang.")
            return False

        self.logger.info(f"✏️ Speichern des Studiengangs: {daten}")
        return self.datenbank.studiengang_speichern(*daten)
        
    def get_studienfortschritt_ansicht_daten(self):
        """
        @brief Ruft die Daten für den Studienfortschritt aus der Datenbank ab.

        @return Eine Liste mit den Studienfortschritts-Daten.
        """
        return self.get_daten_ansicht("studienfortschritt")
    
    def get_zeitmanagement_ansicht_daten(self):
        """
        @brief Ruft die Daten für das Zeitmanagement aus der Datenbank ab.

        @return Eine Liste mit den Zeitmanagement-Daten.
        """
        return self.get_daten_ansicht("zeitmanagement")
    
    def get_einstellungen_ansicht_daten(self):
        """
        @brief Ruft die Daten für die Einstellungen aus der Datenbank ab.

        @return Eine Liste mit den gespeicherten Einstellungen.
        """
        return self.get_daten_ansicht("einstellungen")
    
    def set_einstellungen_ansicht_daten(self, aktion: str, daten: tuple = None) -> bool:
        """
        @brief Setzt oder löscht die Einstellungen in der Datenbank.

        @param aktion Die gewünschte Aktion ("UPDATE" oder "DELETE").
        @param daten Ein Tupel mit den neuen Einstellungen (optional für UPDATE).
        @return True, wenn die Aktion erfolgreich war, sonst False.
        """
        return self.datenbank.einstellungen_verwalten(aktion, daten)