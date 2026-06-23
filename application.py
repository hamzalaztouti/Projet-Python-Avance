"""
application.py - Partie 1 : Application desktop Météo Paris
Projet Python Avancé - Hamza Laztouti/Tahiri rossaina 
Source : API Open-Meteo (données météo temps réel)
"""

# IMPORTS
import tkinter as tk
from tkinter import messagebox
import urllib.request
import json
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# PALETTE DE COULEURS

C = {
    "bg":           "#0F1923",   
    "panneau":      "#162030",  
    "carte":        "#1E2D42",   
    "accent":       "#2D7DD2",  
    "accent2":      "#1A5FA8",   
    "vert":         "#27A969",   
    "orange":       "#E07B39",   
    "rouge":        "#C0392B",   
    "texte":        "#D4DFF0",   
    "texte2":       "#6B83A0",   
    "bordure":      "#243447",   
    "ligne":        "#2D7DD2",   
}

F = {
    "titre":    ("Segoe UI", 17, "bold"),
    "sous":     ("Segoe UI", 9),
    "label":    ("Segoe UI", 9, "bold"),
    "normal":   ("Segoe UI", 10),
    "mono":     ("Consolas", 10),
    "btn":      ("Segoe UI", 10, "bold"),
}

# BASE DE DONNÉES


def init_base():
    """Crée la table météo si elle n'existe pas."""
    try:
        conn = sqlite3.connect("meteo.db")
        curseur = conn.cursor()
        curseur.execute("""
            CREATE TABLE IF NOT EXISTS meteo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                temperature_max REAL,
                temperature_min REAL,
                precipitation REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erreur", "Impossible d'initialiser la base : " + str(e))


def effacer_base():
    """Efface toutes les données de la base et réinitialise l'affichage."""
    try:
        conn = sqlite3.connect("meteo.db")
        curseur = conn.cursor()
        curseur.execute("DELETE FROM meteo")
        conn.commit()
        conn.close()
        _vider_zone(zone_texte)
        _vider_zone(zone_agregation)
        for widget in cadre_graphique.winfo_children():
            widget.destroy()
        set_statut("Base de données effacée.", C["rouge"])
    except Exception as e:
        messagebox.showerror("Erreur", "Impossible d'effacer la base : " + str(e))


def _vider_zone(widget):
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.config(state="disabled")


# TÉLÉCHARGEMENT AVEC THREAD


def telecharger_donnees():
    """Lance le téléchargement dans un thread pour ne pas bloquer l'interface."""
    set_statut("Téléchargement en cours...", C["orange"])
    btn_telecharger.config(state="disabled", bg=C["accent2"])
    threading.Thread(target=_telecharger_worker, daemon=True).start()


def _telecharger_worker():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=48.85&longitude=2.35"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            "&timezone=Europe/Paris&forecast_days=7"
        )
        requete = urllib.request.Request(url)
        reponse = urllib.request.urlopen(requete)
        donnees = json.loads(reponse.read())

        conn = sqlite3.connect("meteo.db")
        curseur = conn.cursor()
        curseur.execute("SELECT COUNT(*) FROM meteo")
        nb = curseur.fetchone()[0]

        if nb > 0:
            fenetre.after(0, lambda: _demander_effacer(conn, curseur, donnees))
            return

        _inserer_donnees(conn, curseur, donnees)

    except Exception as e:
        fenetre.after(0, lambda: messagebox.showerror("Erreur réseau", str(e)))
        fenetre.after(0, _reactiver_btn)


def _demander_effacer(conn, curseur, donnees):
    rep = messagebox.askyesno(
        "Base non vide",
        "La base contient déjà des données.\nVoulez-vous les remplacer ?"
    )
    if rep:
        curseur.execute("DELETE FROM meteo")
        _inserer_donnees(conn, curseur, donnees)
    else:
        conn.close()
        set_statut("Téléchargement annulé.", C["texte2"])
        _reactiver_btn()


def _inserer_donnees(conn, curseur, donnees):
    dates          = donnees["daily"]["time"]
    temps_max      = donnees["daily"]["temperature_2m_max"]
    temps_min      = donnees["daily"]["temperature_2m_min"]
    precipitations = donnees["daily"]["precipitation_sum"]

    for i in range(len(dates)):
        curseur.execute(
            "INSERT INTO meteo (date, temperature_max, temperature_min, precipitation) "
            "VALUES (?, ?, ?, ?)",
            (dates[i], temps_max[i], temps_min[i], precipitations[i])
        )

    conn.commit()
    conn.close()
    fenetre.after(0, lambda: set_statut("Données téléchargées et sauvegardées.", C["vert"]))
    fenetre.after(0, afficher_donnees)
    fenetre.after(0, afficher_agregation)
    fenetre.after(0, afficher_graphique)
    fenetre.after(0, _reactiver_btn)


def _reactiver_btn():
    btn_telecharger.config(state="normal", bg=C["accent"])


# AFFICHAGE DONNÉES

def afficher_donnees():
    try:
        zone_texte.config(state="normal")
        zone_texte.delete("1.0", tk.END)
        conn = sqlite3.connect("meteo.db")
        curseur = conn.cursor()
        curseur.execute("SELECT date, temperature_max, temperature_min, precipitation FROM meteo")
        lignes = curseur.fetchall()
        conn.close()
        for ligne in lignes:
            zone_texte.insert(tk.END,
                "  " + ligne[0]
                + "     Max : " + str(ligne[1]) + " °C"
                + "     Min : " + str(ligne[2]) + " °C"
                + "     Précipitations : " + str(ligne[3]) + " mm\n"
            )
        zone_texte.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Erreur", "Impossible d'afficher les données : " + str(e))


# AGRÉGATION

def afficher_agregation():
    try:
        conn = sqlite3.connect("meteo.db")
        curseur = conn.cursor()
        curseur.execute(
            "SELECT AVG(temperature_max), AVG(temperature_min), SUM(precipitation) FROM meteo"
        )
        result = curseur.fetchone()
        conn.close()

        zone_agregation.config(state="normal")
        zone_agregation.delete("1.0", tk.END)

        if result[0] is None:
            zone_agregation.insert(tk.END, "  Aucune donnée dans la base.")
        else:
            sep = "  " + "─" * 50 + "\n"
            zone_agregation.insert(tk.END, "  RÉSUMÉ STATISTIQUE  —  Requête SQL (AVG / SUM)\n")
            zone_agregation.insert(tk.END, sep)
            zone_agregation.insert(tk.END, "  Moyenne température maximale  :  " + str(round(result[0], 1)) + " °C\n")
            zone_agregation.insert(tk.END, "  Moyenne température minimale  :  " + str(round(result[1], 1)) + " °C\n")
            zone_agregation.insert(tk.END, "  Total des précipitations      :  " + str(round(result[2], 1)) + " mm\n")

        zone_agregation.config(state="disabled")
        set_statut("Agrégation affichée.", C["vert"])
    except Exception as e:
        messagebox.showerror("Erreur", "Impossible d'afficher l'agrégation : " + str(e))


# GRAPHIQUE

def afficher_graphique():
    try:
        conn = sqlite3.connect("meteo.db")
        curseur = conn.cursor()
        curseur.execute("SELECT date, temperature_max, temperature_min FROM meteo")
        lignes = curseur.fetchall()
        conn.close()

        if not lignes:
            messagebox.showinfo("Graphique", "Aucune donnée à afficher.\nTéléchargez d'abord les données.")
            return

        dates     = [l[0] for l in lignes]
        temps_max = [l[1] for l in lignes]
        temps_min = [l[2] for l in lignes]

        fig, ax = plt.subplots(figsize=(9, 3.4))
        fig.patch.set_facecolor(C["panneau"])
        ax.set_facecolor(C["carte"])

        ax.plot(dates, temps_max, marker="o", color="#E05C5C",
                linewidth=2, markersize=6, label="Temp. max", zorder=3)
        ax.plot(dates, temps_min, marker="o", color=C["accent"],
                linewidth=2, markersize=6, label="Temp. min", zorder=3)
        ax.fill_between(dates, temps_max, temps_min,
                        alpha=0.10, color=C["accent"])

        ax.set_title("Températures à Paris — 7 prochains jours",
                     color=C["texte"], fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel("Date", color=C["texte2"], fontsize=9)
        ax.set_ylabel("Température (°C)", color=C["texte2"], fontsize=9)

        ax.tick_params(colors=C["texte2"], labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(C["bordure"])

        ax.grid(True, color=C["bordure"], linestyle="--", linewidth=0.6, alpha=0.8)
        ax.legend(facecolor=C["panneau"], labelcolor=C["texte"],
                  edgecolor=C["bordure"], fontsize=9)

        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        for widget in cadre_graphique.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=cadre_graphique)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
        set_statut("Graphique affiché.", C["vert"])
    except Exception as e:
        messagebox.showerror("Erreur", "Impossible d'afficher le graphique : " + str(e))


# BARRE DE STATUT


def set_statut(message, couleur=None):
    barre_statut.config(
        text="   " + message,
        fg=couleur if couleur else C["texte2"]
    )


# OPTIONS

def changer_theme(bg, panneau, carte):
    """Applique un thème de couleur à toute l'interface."""
    try:
        C["bg"]      = bg
        C["panneau"] = panneau
        C["carte"]   = carte
        fenetre.config(bg=bg)
        entete.config(bg=panneau)
        label_titre.config(bg=panneau)
        label_sous_titre.config(bg=panneau)
        ligne_accent.config(bg=C["ligne"])
        cadre_boutons.config(bg=bg)
        cadre_donnees.config(bg=bg)
        label_donnees.config(bg=bg)
        zone_texte.config(bg=carte)
        cadre_agregation.config(bg=bg)
        label_agregation.config(bg=bg)
        zone_agregation.config(bg=carte)
        cadre_graphique.config(bg=bg)
        label_graphique.config(bg=bg)
        barre_statut.config(bg=panneau)
        set_statut("Thème appliqué.", C["accent"])
    except Exception as e:
        messagebox.showerror("Erreur", "Impossible de changer le thème : " + str(e))


def changer_police(police, taille):
    try:
        zone_texte.config(font=(police, taille))
        zone_agregation.config(font=(police, taille))
        set_statut("Police : " + police + "  " + str(taille) + " pt", C["accent"])
    except Exception as e:
        messagebox.showerror("Erreur", "Impossible de changer la police : " + str(e))


# CONSTRUCTION DE L'INTERFACE

fenetre = tk.Tk()
fenetre.title("Météo Paris — Application Python Avancé")
fenetre.geometry("1050x830")
fenetre.config(bg=C["bg"])
fenetre.resizable(True, True)

# MENU
def make_menu(parent):
    return tk.Menu(parent, tearoff=0,
                   bg=C["panneau"], fg=C["texte"],
                   activebackground=C["accent"],
                   activeforeground="white")

menu_bar = tk.Menu(fenetre, bg=C["panneau"], fg=C["texte"],
                   activebackground=C["accent"], activeforeground="white",
                   relief="flat")

menu_donnees = make_menu(menu_bar)
menu_donnees.add_command(label="Télécharger les données", command=telecharger_donnees)
menu_donnees.add_command(label="Effacer la base",         command=effacer_base)
menu_donnees.add_separator()
menu_donnees.add_command(label="Quitter",                 command=fenetre.quit)
menu_bar.add_cascade(label="Données", menu=menu_donnees)

menu_options = make_menu(menu_bar)

menu_themes = make_menu(menu_options)
menu_themes.add_command(label="Sombre — Bleu (défaut)",
    command=lambda: changer_theme("#0F1923", "#162030", "#1E2D42"))
menu_themes.add_command(label="Sombre — Gris",
    command=lambda: changer_theme("#1A1A1A", "#242424", "#2E2E2E"))
menu_themes.add_command(label="Clair — Blanc",
    command=lambda: changer_theme("#F2F5FA", "#FFFFFF", "#E8EDF5"))
menu_themes.add_command(label="Sombre — Vert",
    command=lambda: changer_theme("#0D1F17", "#122A1E", "#1A3D2B"))
menu_options.add_cascade(label="Thème", menu=menu_themes)

menu_polices = make_menu(menu_options)
menu_polices.add_command(label="Consolas 10 (défaut)",  command=lambda: changer_police("Consolas", 10))
menu_polices.add_command(label="Courier New 10",        command=lambda: changer_police("Courier New", 10))
menu_polices.add_command(label="Arial 10",              command=lambda: changer_police("Arial", 10))
menu_polices.add_command(label="Arial 12",              command=lambda: changer_police("Arial", 12))
menu_polices.add_command(label="Helvetica 11",          command=lambda: changer_police("Helvetica", 11))
menu_options.add_cascade(label="Police du texte", menu=menu_polices)

menu_bar.add_cascade(label="Options", menu=menu_options)
fenetre.config(menu=menu_bar)

# EN-TÊTE
entete = tk.Frame(fenetre, bg=C["panneau"], pady=16)
entete.pack(fill="x")

label_titre = tk.Label(
    entete,
    text="Météo Paris — 7 prochains jours",
    font=F["titre"],
    bg=C["panneau"],
    fg=C["texte"]
)
label_titre.pack()

label_sous_titre = tk.Label(
    entete,
    text="Source : Open-Meteo API   •   Stockage : SQLite   •   Projet Python Avancé",
    font=F["sous"],
    bg=C["panneau"],
    fg=C["texte2"]
)
label_sous_titre.pack(pady=(3, 0))

# Ligne décorative
ligne_accent = tk.Frame(fenetre, height=2, bg=C["ligne"])
ligne_accent.pack(fill="x")

# BOUTONS
cadre_boutons = tk.Frame(fenetre, bg=C["bg"], pady=14)
cadre_boutons.pack()

def creer_bouton(parent, texte, commande, couleur):
    return tk.Button(
        parent,
        text=texte,
        command=commande,
        bg=couleur,
        fg="white",
        font=F["btn"],
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=9,
        width=18,
        bd=0,
        activebackground=C["accent2"],
        activeforeground="white"
    )

btn_telecharger = creer_bouton(cadre_boutons, "⬇  Télécharger",  telecharger_donnees, C["accent"])
btn_agregation  = creer_bouton(cadre_boutons, "▦  Agrégation",   afficher_agregation, C["vert"])
btn_graphique   = creer_bouton(cadre_boutons, "↗  Graphique",    afficher_graphique,  C["orange"])
btn_effacer     = creer_bouton(cadre_boutons, "✕  Effacer",      effacer_base,        C["rouge"])

btn_telecharger.grid(row=0, column=0, padx=8)
btn_agregation .grid(row=0, column=1, padx=8)
btn_graphique  .grid(row=0, column=2, padx=8)
btn_effacer    .grid(row=0, column=3, padx=8)

# SECTION DONNÉES
cadre_donnees = tk.Frame(fenetre, bg=C["bg"])
cadre_donnees.pack(fill="x", padx=16, pady=(0, 6))

label_donnees = tk.Label(
    cadre_donnees,
    text="DONNÉES DE LA BASE",
    font=F["label"],
    bg=C["bg"],
    fg=C["accent"],
    anchor="w"
)
label_donnees.pack(fill="x", pady=(0, 3))

zone_texte = tk.Text(
    cadre_donnees,
    height=7,
    state="disabled",
    font=F["mono"],
    bg=C["carte"],
    fg=C["texte"],
    relief="flat",
    bd=0,
    padx=10,
    pady=6,
    selectbackground=C["accent"],
    insertbackground=C["texte"]
)
zone_texte.pack(fill="x")

# SECTION AGRÉGATION
cadre_agregation = tk.Frame(fenetre, bg=C["bg"])
cadre_agregation.pack(fill="x", padx=16, pady=(10, 6))

label_agregation = tk.Label(
    cadre_agregation,
    text="RÉSUMÉ AGRÉGÉ  —  REQUÊTE SQL",
    font=F["label"],
    bg=C["bg"],
    fg=C["accent"],
    anchor="w"
)
label_agregation.pack(fill="x", pady=(0, 3))

zone_agregation = tk.Text(
    cadre_agregation,
    height=5,
    state="disabled",
    font=F["mono"],
    bg=C["carte"],
    fg=C["texte"],
    relief="flat",
    bd=0,
    padx=10,
    pady=6,
    selectbackground=C["accent"],
    insertbackground=C["texte"]
)
zone_agregation.pack(fill="x")

# SECTION GRAPHIQUE
label_graphique = tk.Label(
    fenetre,
    text="GRAPHIQUE DES TEMPÉRATURES",
    font=F["label"],
    bg=C["bg"],
    fg=C["accent"],
    anchor="w"
)
label_graphique.pack(fill="x", padx=16, pady=(10, 3))

cadre_graphique = tk.Frame(fenetre, bg=C["bg"])
cadre_graphique.pack(fill="both", expand=True, padx=16, pady=(0, 6))

# BARRE DE STATUT
barre_statut = tk.Label(
    fenetre,
    text="   Prêt.",
    font=F["sous"],
    bg=C["panneau"],
    fg=C["texte2"],
    anchor="w",
    pady=5
)
barre_statut.pack(side="bottom", fill="x")

# INIT
init_base()
afficher_donnees()
afficher_agregation()
fenetre.mainloop()