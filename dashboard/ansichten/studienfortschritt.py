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
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Studienfortschritt")

        self.logger.info("📊 Studienfortschritt geladen.")
        self.daten = self.master.logik.get_studienfortschritt_ansicht_daten()

        ttk.Label(self, text="📈 Studienfortschritt", font=("Arial", 16)).pack(pady=10)

        if not self.daten:
            messagebox.showinfo("Keine Daten", "Es sind keine Verlaufsdaten verfügbar.")
            self.logger.warning("⚠️ Keine Verlaufsdaten gefunden.")
            return

        self.plot_fortschritt()

    def plot_fortschritt(self):
        """Erstellt das Diagramm für den Studienfortschritt mit verschiedenen Symbolen für die Modulstatus."""
        self.logger.info("📊 Erstelle Diagramm für Studienfortschritt...")

        daten = self.daten
        daten.sort(key=lambda x: x[3])

        x_werte = [datetime.datetime.strptime(d[3], "%Y-%m-%d") for d in daten]
        y_offen = np.array([int(d[0]) for d in daten])
        y_bearbeitung = np.array([int(d[1]) for d in daten])
        y_abgeschlossen = np.array([int(d[2]) for d in daten])
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(
            x_werte, y_offen, marker="o", linestyle="-", label="Offene Module", color="red", alpha=0.8
        )
        ax.plot(
            x_werte, y_bearbeitung, marker="s", linestyle="-", label="In Bearbeitung", color="orange", alpha=0.8
        )
        ax.plot(
            x_werte, y_abgeschlossen, marker="^", linestyle="-", label="Abgeschlossen", color="green", alpha=0.8
        )

        ax.set_xlabel("Datum")
        ax.set_ylabel("Anzahl Module")
        ax.set_title("Studienfortschritt über die Zeit")
        ax.legend()
        ax.grid(True)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(x_werte) // 10)))
        plt.xticks(rotation=45)

        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

        self.logger.info("✅ Diagramm erfolgreich erstellt und eingebunden.")