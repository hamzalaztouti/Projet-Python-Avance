# Projet Python Avance

Application desktop meteo + Analyse litteraire et generation de rapport Word
Hamza Laztouti et Tahiri Rossaina — Ynov Campus — 2024/2025

---

## Description

Ce projet est compose de deux parties independantes.

Partie 1 — Application desktop Tkinter affichant les previsions meteo de Paris sur 7 jours via une API JSON, avec stockage SQLite, agregation SQL et graphique integre.

Partie 2 — Script d'analyse textuelle du roman Les Miserables de Victor Hugo telecharge depuis Project Gutenberg, avec generation automatique d'un rapport Word illustre.

---

## Structure du projet

    application.py              Partie 1 : Application desktop meteo
    main.py                     Partie 2 : Analyse + rapport Word
    test_fonctions.py           Tests unitaires
    meteo.db                    Base de donnees SQLite
    les_miserables.txt          Livre telecharge depuis Gutenberg
    graphique_chapitre1.png     Graphique genere
    image1.jpg                  Image telechargee
    image1_modifiee.jpg         Image recadree et redimensionnee
    image1_avec_logo.jpg        Image avec logo colle
    logo.png                    Logo VH genere
    rapport_les_miserables.docx Rapport Word final

---

## Installation des dependances

    pip install pillow matplotlib python-docx

---

## Lancement

Partie 1 — Application meteo :

    python application.py

Partie 2 — Rapport Word :

    python main.py

Tests unitaires :

    python -m unittest test_fonctions.py -v

---

## Partie 1 — Application Desktop Meteo

### Fonctionnalites

- Telechargement des donnees meteo depuis Open-Meteo API au format JSON
- Stockage dans une base de donnees SQLite
- Gestion de la base non vide avec popup de confirmation
- Affichage de l'agregation SQL : moyenne des temperatures, total des precipitations
- Graphique des temperatures integre dans la fenetre via Matplotlib
- Barre de statut en bas indiquant l'etat de chaque operation
- Menu Options avec changement de theme (4 themes) et de police (5 polices)
- Telechargement dans un thread separe pour ne pas bloquer l'interface
- Gestion des exceptions sur toutes les fonctions

### Boutons de l'interface

    Telecharger      Recupere les donnees meteo et les stocke en base
    Agregation       Affiche la moyenne et le total via requete SQL
    Graphique        Affiche la courbe des temperatures sur 7 jours
    Effacer          Vide la base de donnees et reinitialise l'affichage

### Source des donnees

API Open-Meteo, gratuite et sans cle API.
Localisation : Paris (48.85 N, 2.35 E).
Donnees : temperature maximale, temperature minimale, precipitations sur 7 jours.

---

## Partie 2 — Analyse Litteraire et Rapport Word

### Fonctionnalites

- Telechargement automatique des Miserables depuis Project Gutenberg
- Extraction du titre, de l'auteur et du Chapitre I
- Comptage des mots par paragraphe, arrondi a la dizaine inferieure
- Tri et calcul des occurrences par longueur de paragraphe
- Generation d'un graphique de distribution en barres
- Telechargement d'une image de couverture depuis Internet
- Recadrage et redimensionnement de l'image avec PIL
- Creation d'un logo noir et blanc avec les initiales VH, rotation 45 degres et collage sur l'image
- Generation d'un rapport Word de 3 pages avec mise en page professionnelle

### Contenu du rapport Word

    Page 1     Titre, image avec logo, auteur de l'oeuvre, auteurs du rapport
    Page 2     Graphique de distribution et description statistique
    Page 3     Chiffres cles, source des donnees, note methodologique

---

## Tests Unitaires

8 tests couvrant les fonctions principales :

    test_extraction_titre          Extraction du titre depuis les metadonnees Gutenberg
    test_extraction_auteur         Extraction de l'auteur
    test_arrondi_dizaine           Arrondi a la dizaine inferieure
    test_comptage_mots             Comptage de mots dans un paragraphe
    test_paragraphes_non_vides     Filtrage des paragraphes vides
    test_insertion                 Insertion d'un enregistrement dans SQLite
    test_effacer                   Suppression des donnees de la base
    test_agregation                Calcul AVG et SUM via SQL

---

## Technologies utilisees

    tkinter            Interface graphique desktop
    sqlite3            Base de donnees locale
    urllib.request     Telechargement de donnees JSON et de fichiers
    json               Parsing des donnees API
    matplotlib         Generation de graphiques
    PIL (Pillow)       Traitement d'images
    python-docx        Generation du rapport Word
    threading          Telechargement non bloquant
    unittest           Tests unitaires

---

## Auteurs

Hamza Laztouti
Tahiri Rossaina

---

## Contexte academique

Projet realise dans le cadre du cours Python Avance.
Ynov Campus — Bachelor 3 Data et Intelligence Artificielle — 2024/2025