import sqlite3
import os
from datetime import datetime

class DbManager:
    def __init__(self, db_path="gestion_achats.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Crée la base de données et les tables si elles n'existent pas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. Table Stock (Inventaire des produits)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            categorie TEXT,
            quantite INTEGER NOT NULL DEFAULT 0,
            prix_unitaire REAL NOT NULL DEFAULT 0.0,
            seuil_alerte INTEGER DEFAULT 5
        )
        """)
        
        # Initialisation de quelques produits si la table est vide
        cursor.execute("SELECT COUNT(*) FROM stock")
        if cursor.fetchone()[0] == 0:
            initial_products = [
                ("T-shirt Pro", "Vêtements", 50, 20.00, 10),
                ("Smartphone X", "Électronique", 15, 300.00, 5),
                ("Lampe de bureau", "Maison", 0, 15.00, 10)
            ]
            cursor.executemany("""
            INSERT INTO stock (nom, categorie, quantite, prix_unitaire, seuil_alerte) 
            VALUES (?, ?, ?, ?, ?)
            """, initial_products)

        # 2. Table Factures d'Achats (Réception de marchandises et mise à jour du stock)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS factures_achats (
            id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL UNIQUE,
            date_reception DATE NOT NULL,
            fournisseur TEXT NOT NULL,
            montant_total REAL NOT NULL,
            statut TEXT NOT NULL, -- 'Payée', 'En attente'
            utilisateur TEXT
        )
        """)

        # 3. Table des Lignes de Facture (Détails des produits achetés)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lignes_factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facture_id INTEGER,
            produit_id INTEGER,
            quantite_achetee INTEGER NOT NULL,
            prix_achat_unitaire REAL NOT NULL,
            FOREIGN KEY (facture_id) REFERENCES factures_achats(id_facture),
            FOREIGN KEY (produit_id) REFERENCES stock(id)
        )
        """)

        conn.commit()
        conn.close()
        
    def get_all_products(self):
        """Récupère tous les produits en stock."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stock ORDER BY nom")
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    # ... autres méthodes (ajouter produit, get_produit_par_id, etc.) seront nécessaires.