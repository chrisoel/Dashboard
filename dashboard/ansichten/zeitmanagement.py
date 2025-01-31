import tkinter as tk
from tkinter import ttk, messagebox
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta


class Zeitmanagement(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Zeitmanagement")

        self.logger.info("📅 Zeitmanagement geladen.")
        self.erstelle_gui()
        self.lade_daten()

    def erstelle_gui(self):
        """Erstellt die GUI-Struktur für das Zeitmanagement."""
        ttk.Label(self, text="⏳ Zeitmanagement", font=("Arial", 16)).pack(pady=10)
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(pady=5, fill=tk.X)

    def lade_daten(self):
        """Lädt die Daten für das Zeitmanagement aus der Datenbank."""
        daten = self.master.logik.get_zeitmanagement_ansicht_daten()

        if not daten:
            messagebox.showinfo("Keine Daten", "Es sind keine Zeitmanagement-Daten verfügbar.")
            self.logger.warning("⚠️ Keine Zeitmanagement-Daten gefunden.")
            return

        self.anzeige_zeitmanagement(daten[0])

    def anzeige_zeitmanagement(self, daten):
        """Zeigt das Zeitmodell und berechnet das Studienpensum."""
        studiengang, zeitmodell, studienstart, aktuelle_ects, module_gesamt = daten

        # GUI-Elemente
        ttk.Label(self.info_frame, text=f"📚 Studiengang: {studiengang}").pack(anchor="w", pady=2)
        ttk.Label(self.info_frame, text=f"📅 Studienbeginn: {studienstart}").pack(anchor="w", pady=2)
        ttk.Label(self.info_frame, text=f"📖 Zeitmodell: {zeitmodell}").pack(anchor="w", pady=2)

        # Berechnung des Studienfortschritts
        geplante_stunden_pro_woche, aktuelle_ects_pro_woche, prognose_ende = self.berechne_studienpensum(
            zeitmodell, studienstart, aktuelle_ects, module_gesamt
        )

        prognose_text = prognose_ende.strftime("%d.%m.%Y") if prognose_ende else "Unbekannt (kein Fortschritt)"
        ttk.Label(self.info_frame, text=f"🎯 Erwartetes Studienende: {prognose_text}").pack(anchor="w", pady=2)

        # Diagramm erzeugen
        self.erstelle_wochenstunden_diagramm(geplante_stunden_pro_woche, aktuelle_ects_pro_woche)

        # Warnungen anzeigen
        self.prüfe_lerntempo(geplante_stunden_pro_woche, aktuelle_ects_pro_woche)

    def berechne_studienpensum(self, zeitmodell, studienstart, aktuelle_ects, module_gesamt):
        """Berechnet die wöchentlichen Lernzeiten und das voraussichtliche Studienende."""
        gesamt_ects = 180
        semesterdauer = 6 if zeitmodell == "Vollzeit" else (8 if zeitmodell == "TeilzeitI" else 12)
        ects_pro_semester = gesamt_ects / semesterdauer
        wochen_pro_semester = semesterdauer * 4
        stunden_pro_ects = 25  # IU Empfehlung: 25-30 Stunden pro 5 ECTS
        geplante_stunden_pro_woche = (ects_pro_semester * stunden_pro_ects / 5) / wochen_pro_semester

        if module_gesamt > 0 and aktuelle_ects > 0:
            aktuelle_ects_pro_woche = aktuelle_ects / ((module_gesamt / semesterdauer) * wochen_pro_semester)
        else:
            aktuelle_ects_pro_woche = 0

        prognose_ende = None
        if aktuelle_ects_pro_woche > 0:
            startdatum_dt = datetime.strptime(studienstart, "%Y-%m-%d")
            wochen_bis_abschluss = (gesamt_ects - aktuelle_ects) / aktuelle_ects_pro_woche
            prognose_ende = startdatum_dt + timedelta(weeks=wochen_bis_abschluss)

        return geplante_stunden_pro_woche, aktuelle_ects_pro_woche, prognose_ende

    def erstelle_wochenstunden_diagramm(self, geplante_stunden, aktuelle_stunden):
        """Erstellt ein Balkendiagramm für die geplanten und tatsächlichen Lernzeiten."""
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Geplante Stunden", "Aktuelle Stunden"], [geplante_stunden, aktuelle_stunden], 
               color=["blue", "green"])
        ax.set_ylabel("Stunden/Woche")
        ax.set_title("Vergleich: Geplante vs. Tatsächliche Lernstunden")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

    def prüfe_lerntempo(self, geplante_stunden, aktuelle_stunden):
        """Zeigt Hinweise oder Warnungen basierend auf dem aktuellen Lernfortschritt an."""
        if aktuelle_stunden == 0:
            messagebox.showwarning("🚨 Achtung", "Es wurde noch kein Fortschritt erfasst. Bitte Module abschließen.")
            self.logger.warning("⚠️ Keine ECTS bisher abgeschlossen.")
        elif aktuelle_stunden < geplante_stunden * 0.8:
            messagebox.showwarning("⚠️ Warnung", "Ihr aktuelles Lerntempo liegt unter dem Plan! Erwägen Sie, mehr Lernzeit einzuplanen.")
            self.logger.warning("⚠️ Nutzer lernt langsamer als geplant.")
        elif aktuelle_stunden > geplante_stunden * 1.2:
            messagebox.showinfo("🎯 Hinweis", "Sie liegen über dem geplanten Tempo! Möglicherweise können Sie Ihr Studium früher abschließen.")
            self.logger.info("✅ Nutzer ist schneller als geplant.")