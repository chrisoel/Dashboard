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
        daten = self.master.logik.get_zeitmanagement_ansicht_daten()

        ttk.Label(self, text="⏳ Zeitmanagement", font=("Arial", 16)).pack(pady=10)

        if not daten:
            messagebox.showinfo("Keine Daten", "Es sind keine Zeitmanagement-Daten verfügbar.")
            self.logger.warning("⚠️ Keine Zeitmanagement-Daten gefunden.")
            return

        self.anzeige_zeitmanagement(daten)

    def anzeige_zeitmanagement(self, daten):
        """Zeigt das Zeitmodell und berechnet das Studienpensum."""
        studiengang, zeitmodell, studienstart, aktuelle_ects, module_gesamt = daten[0]

        ttk.Label(self, text=f"📚 Studiengang: {studiengang}").pack(pady=5)
        ttk.Label(self, text=f"📅 Studienbeginn: {studienstart}").pack(pady=5)
        ttk.Label(self, text=f"📖 Zeitmodell: {zeitmodell}").pack(pady=5)

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

        startdatum_dt = datetime.strptime(studienstart, "%Y-%m-%d")
        if aktuelle_ects_pro_woche > 0:
            wochen_bis_abschluss = (gesamt_ects - aktuelle_ects) / aktuelle_ects_pro_woche
            prognose_ende = startdatum_dt + timedelta(weeks=wochen_bis_abschluss)
            prognose_text = prognose_ende.strftime("%d.%m.%Y")
        else:
            prognose_text = "Unbekannt (kein Fortschritt)"

        ttk.Label(self, text=f"🎯 Erwartetes Studienende: {prognose_text}").pack(pady=5)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Geplante Stunden", "Aktuelle Stunden"], [geplante_stunden_pro_woche, aktuelle_ects_pro_woche], 
               color=["blue", "green"])
        ax.set_ylabel("Stunden/Woche")
        ax.set_title("Vergleich: Geplante vs. Tatsächliche Lernstunden")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

        if aktuelle_ects_pro_woche == 0:
            messagebox.showwarning("🚨 Achtung", "Es wurde noch kein Fortschritt erfasst. Bitte Module abschließen.")
            self.logger.warning("⚠️ Keine ECTS bisher abgeschlossen.")
        elif aktuelle_ects_pro_woche < geplante_stunden_pro_woche * 0.8:
            messagebox.showwarning("⚠️ Warnung", "Ihr aktuelles Lerntempo liegt unter dem Plan! Erwägen Sie, mehr Lernzeit einzuplanen.")
            self.logger.warning("⚠️ Nutzer lernt langsamer als geplant.")
        elif aktuelle_ects_pro_woche > geplante_stunden_pro_woche * 1.2:
            messagebox.showinfo("🎯 Hinweis", "Sie liegen über dem geplanten Tempo! Möglicherweise können Sie Ihr Studium früher abschließen.")
            self.logger.info("✅ Nutzer ist schneller als geplant.")