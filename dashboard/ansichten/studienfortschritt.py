"""
@file studienfortschritt.py
@brief Modul zur Visualisierung des Studienfortschritts.

Dieses Modul stellt eine grafische Oberfläche bereit, um den Fortschritt des Studiums 
über die Zeit zu visualisieren. Die Daten werden aus der Datenbank geladen und 
in einem Liniendiagramm dargestellt.

@author CHOE
@date 2025-01-31
@version 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import numpy as np


class Studienfortschritt(ttk.Frame):
    """
    @brief GUI-Komponente zur Darstellung des Studienfortschritts.

    Diese Klasse ermöglicht die Anzeige des Fortschritts im Studium anhand eines Diagramms.
    Die Verlaufsdaten werden aus der Datenbank geladen, verarbeitet und visualisiert.

    @extends ttk.Frame
    """

    def __init__(self, master):
        """
        @brief Initialisiert das Studienfortschritt-Widget.

        Erstellt die grafische Oberfläche für die Anzeige des Studienfortschritts 
        und lädt die Verlaufsdaten aus der Datenbank.

        @param master Das Hauptfenster (tkinter Parent Widget).
        """
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Studienfortschritt")

        self.logger.info("📊 Studienfortschritt geladen.")
        self.erstelle_gui()
        self.lade_daten()

    def erstelle_gui(self):
        """
        @brief Erstellt die GUI-Struktur für den Studienfortschritt.

        Fügt Labels zur Anzeige der Fortschrittsinformationen hinzu.
        """
        ttk.Label(self, text="📈 Studienfortschritt", font=("Arial", 16)).pack(pady=10)

    def lade_daten(self):
        """
        @brief Lädt die Verlaufsdaten aus der Datenbank und verarbeitet sie.

        Falls keine Daten gefunden werden, wird eine Meldung an den Nutzer ausgegeben.
        """
        daten = self.master.logik.get_studienfortschritt_ansicht_daten()

        if not daten:
            messagebox.showinfo("Keine Daten", "Es sind keine Verlaufsdaten verfügbar.")
            self.logger.warning("⚠️ Keine Verlaufsdaten gefunden.")
            return

        x_werte, y_offen, y_bearbeitung, y_abgeschlossen = self.verarbeite_daten(daten)
        self.erstelle_fortschritt_diagramm(x_werte, y_offen, y_bearbeitung, y_abgeschlossen)

    def verarbeite_daten(self, daten):
        """
        @brief Konvertiert die Rohdaten in ein geeignetes Format für die Darstellung.

        @param daten Liste mit Verlaufswerten aus der Datenbank.
        @return Ein Tupel mit Listen: (x_werte, y_offen, y_bearbeitung, y_abgeschlossen).
        """
        self.logger.info("📊 Verarbeite Verlaufsdaten für das Diagramm...")
        daten.sort(key=lambda x: x[3])  # Sortierung nach Datum

        x_werte = [datetime.datetime.strptime(d[3], "%Y-%m-%d") for d in daten]
        y_offen = np.array([int(d[0]) for d in daten])
        y_bearbeitung = np.array([int(d[1]) for d in daten])
        y_abgeschlossen = np.array([int(d[2]) for d in daten])

        return x_werte, y_offen, y_bearbeitung, y_abgeschlossen

    def erstelle_fortschritt_diagramm(self, x_werte, y_offen, y_bearbeitung, y_abgeschlossen):
        """
        @brief Erstellt das Diagramm für den Studienfortschritt.

        Diese Methode visualisiert die Anzahl der offenen, in Bearbeitung befindlichen 
        und abgeschlossenen Module über die Zeit.

        @param x_werte Liste mit Datumseinträgen.
        @param y_offen Anzahl offener Module pro Datum.
        @param y_bearbeitung Anzahl der Module in Bearbeitung pro Datum.
        @param y_abgeschlossen Anzahl abgeschlossener Module pro Datum.
        """
        self.logger.info("📊 Erstelle Diagramm für Studienfortschritt...")

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(x_werte, y_offen, marker="o", linestyle="-", label="Offene Module", color="red", alpha=0.8)
        ax.plot(x_werte, y_bearbeitung, marker="s", linestyle="-", label="In Bearbeitung", color="orange", alpha=0.8)
        ax.plot(x_werte, y_abgeschlossen, marker="^", linestyle="-", label="Abgeschlossen", color="green", alpha=0.8)

        # Layout
        ax.set_xlabel("Datum")
        ax.set_ylabel("Anzahl Module")
        ax.set_title("Studienfortschritt über die Zeit")
        ax.legend()
        ax.grid(True)

        # Datum formatieren
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(x_werte) // 10)))
        plt.xticks(rotation=45)

        # Nur ganze Zahlen auf der Y-Achse
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Diagramm einbinden
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

        self.logger.info("✅ Diagramm erfolgreich erstellt und eingebunden.")