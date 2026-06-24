import unittest
import sqlite3
import os

#  Tests pour main.py 

class TestExtractionTexte(unittest.TestCase):

    def test_extraction_titre(self):
        lignes = ["Title: Les Miserables", "Author: Victor Hugo"]
        titre = ""
        for ligne in lignes:
            if ligne.startswith("Title:"):
                titre = ligne.replace("Title:", "").strip()
        self.assertEqual(titre, "Les Miserables")

    def test_extraction_auteur(self):
        lignes = ["Title: Les Miserables", "Author: Victor Hugo"]
        auteur = ""
        for ligne in lignes:
            if ligne.startswith("Author:"):
                auteur = ligne.replace("Author:", "").strip()
        self.assertEqual(auteur, "Victor Hugo")

    def test_arrondi_dizaine(self):
        self.assertEqual((123 // 10) * 10, 120)
        self.assertEqual((127 // 10) * 10, 120)
        self.assertEqual((130 // 10) * 10, 130)

    def test_comptage_mots(self):
        para = "Bonjour tout le monde voici un test"
        mots = para.split()
        self.assertEqual(len(mots), 7)

    def test_paragraphes_non_vides(self):
        texte = "Para un.\n\nPara deux.\n\n\n\nPara trois."
        paragraphes = texte.split("\n\n")
        paragraphes_valides = [p for p in paragraphes if p.strip() != ""]
        self.assertEqual(len(paragraphes_valides), 3)


# Tests pour application.py 

class TestBaseDonnees(unittest.TestCase):

    def setUp(self):
        # Crée une base de test temporaire
        self.conn = sqlite3.connect("test_meteo.db")
        curseur = self.conn.cursor()
        curseur.execute("""
            CREATE TABLE IF NOT EXISTS meteo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                temperature_max REAL,
                temperature_min REAL,
                precipitation REAL
            )
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        os.remove("test_meteo.db")

    def test_insertion(self):
        curseur = self.conn.cursor()
        curseur.execute(
            "INSERT INTO meteo (date, temperature_max, temperature_min, precipitation) VALUES (?, ?, ?, ?)",
            ("2026-06-06", 21.3, 13.9, 1.8)
        )
        self.conn.commit()
        curseur.execute("SELECT COUNT(*) FROM meteo")
        nb = curseur.fetchone()[0]
        self.assertEqual(nb, 1)

    def test_effacer(self):
        curseur = self.conn.cursor()
        curseur.execute(
            "INSERT INTO meteo (date, temperature_max, temperature_min, precipitation) VALUES (?, ?, ?, ?)",
            ("2026-06-06", 21.3, 13.9, 1.8)
        )
        self.conn.commit()
        curseur.execute("DELETE FROM meteo")
        self.conn.commit()
        curseur.execute("SELECT COUNT(*) FROM meteo")
        nb = curseur.fetchone()[0]
        self.assertEqual(nb, 0)

    def test_agregation(self):
        curseur = self.conn.cursor()
        curseur.execute(
            "INSERT INTO meteo (date, temperature_max, temperature_min, precipitation) VALUES (?, ?, ?, ?)",
            ("2026-06-06", 20.0, 10.0, 2.0)
        )
        curseur.execute(
            "INSERT INTO meteo (date, temperature_max, temperature_min, precipitation) VALUES (?, ?, ?, ?)",
            ("2026-06-07", 22.0, 12.0, 4.0)
        )
        self.conn.commit()
        curseur.execute("SELECT AVG(temperature_max), SUM(precipitation) FROM meteo")
        result = curseur.fetchone()
        self.assertEqual(result[0], 21.0)
        self.assertEqual(result[1], 6.0)


if __name__ == "__main__":
    unittest.main()