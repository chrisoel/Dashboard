"""
@file ansicht_enum.py
@brief Enthält die Enumeration für verschiedene Anzeigetypen in der Anwendung.

Dieses Modul definiert die verschiedenen Ansichten, die in der Anwendung verwendet werden. 
Die `AnsichtTyp`-Enum wird zur Steuerung der GUI-Ansicht verwendet.

@author CHOE
@date 2025-01-31
@version 1.0
"""

from enum import Enum

class AnsichtTyp(Enum):
    """
    @brief Enumeration für verschiedene Anzeigetypen in der Anwendung.

    Diese Enum-Klasse definiert verschiedene Ansichten, die in der Anwendung verwendet werden.

    Attribute:
        STARTBILDSCHIRM (str): Startbildschirm der Anwendung.
        MODULUEBERSICHT (str): Übersicht über die Module.
        STUDIENFORTSCHRITT (str): Anzeige des Studienfortschritts.
        ZEITMANAGEMENT (str): Verwaltung der Zeitplanung.
        EINSTELLUNGEN (str): Zugriff auf die Anwendungseinstellungen.
    """
    STARTBILDSCHIRM = "Startbildschirm"
    MODULUEBERSICHT = "Modulübersicht"
    STUDIENFORTSCHRITT = "Studienfortschritt"
    ZEITMANAGEMENT = "Zeitmanagement"
    EINSTELLUNGEN = "Einstellungen"