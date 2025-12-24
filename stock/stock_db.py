
from datetime import datetime
from fonction.methode  import cal
class DBServiceMixin:
    def __init__(self, dbfolder: str):
        self.dbfolder = dbfolder
        self.cal = cal()

    def get_connection(self):
        return self.cal.connect_to_db(self.dbfolder)
    
class DataManage(DBServiceMixin):
    def init_db(self):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        # Table produits
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                ref INTEGER PRIMARY UNIQUE,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                price REAL DEFAULT 0,
                alert_min INTEGER DEFAULT 5,
                created_at TEXT
            )
        """)

        # Historique des ajustements
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                old_qty INTEGER,
                new_qty INTEGER,
                type TEXT,
                user TEXT,
                date TEXT,
                comment TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)

        conn.commit()
        conn.close()
    # Ajouter un nouveau produit
    def add_product(self,ref,name, category, quantity, price, price_vent, alert_min):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO products (ref,name, category, price,price_vent, alert_min, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ref,name, category,  price, price_vent, alert_min, datetime.now().isoformat()))
        cur.execute("""
            INSERT INTO stock (id_libelle, qty,price,price_vente)
                    VALUES (?, ?, ?, ?)""", (ref, quantity, price, price_vent))
        conn.commit()
        conn.close()
    # Mettre à jour la quantité d'un produit
    def update_product(self,product_id, name, category, quantity, price, alert_min):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        # récupérer ancienne quantité
        # cur.execute("SELECT quantity FROM products WHERE ref=?", (product_id,))
        # old_qty = cur.fetchone()[0]

        # mise à jour
        cur.execute("""
            UPDATE products
            SET name=?, category=?, quantity=?, price=?, alert_min=?
            WHERE ref=?
        """, (name, category, quantity, price, alert_min, product_id))

        conn.commit()
        conn.close()

        # # enregistrer dans l'historique
        # if old_qty != quantity:
        #     add_history(product_id, old_qty, quantity, "Modification", user="Admin")


    # Récupérer tous les produits
    def get_all_products(self):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                p.ref,
                p.name,
                p.category,
                COALESCE(s.qty,0) as qty,
                p.price,
                p.price_vent,
                p.alert_min
            FROM products p
            LEFT JOIN stock s ON s.id_libelle = p.ref
            ORDER BY p.name ASC
        """)


        rows = cur.fetchall()
        
        conn.close()
        cols = ['ref','produit','categorie','qty','price','price_vent','alert_min']
        
        return [dict(zip(cols, r)) for r in rows]
    

    # Récupérer les produits en dessous du seuil d'alerte
    def get_low_stock_products(self):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("""
            SELECT ref, name, category, quantity, price, alert_min
            FROM products
            WHERE quantity <= alert_min
            ORDER BY quantity ASC
        """)

        rows = cur.fetchall()
        conn.close()
        return rows

    # Ajouter une entrée dans l'historique des ajustements
    def add_history(self,product_id, old_qty, new_qty, movement_type, user="SYSTEM", comment=""):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO stock_history (product_id, old_qty, new_qty, type, user, date, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, old_qty, new_qty, movement_type, user, datetime.now().isoformat(), comment))

        conn.commit()
        conn.close()

    def get_all_history(self):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("""
            SELECT h.date, p.name, h.old_qty, h.new_qty, h.type, h.user, h.comment
            FROM stock_history h
            JOIN products p ON p.ref = h.product_id
            ORDER BY h.date DESC
        """)

        rows = cur.fetchall()
        conn.close()
        return rows

    # Récupérer l'historique pour un produit spécifique
    def get_history_for_product(self,product_id):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("""
            SELECT h.date, p.name, h.old_qty, h.new_qty, h.type, h.user, h.comment
            FROM stock_history h
            JOIN products p ON p.ref = h.product_id
            WHERE product_id=?
            ORDER BY h.date DESC
        """, (product_id,))

        rows = cur.fetchall()
        conn.close()
        return rows

    # Récupérer un produit par son ID
    def get_product_by_id(self,pid):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()
        cur.execute("SELECT ref, name, category, price, alert_min FROM products WHERE ref=?", (pid,))
        row = cur.fetchone()
        conn.close()
        return row

    # Supprimer un produit
    def delete_product(self,product_id):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("DELETE FROM products WHERE ref=?", (product_id,))

        conn.commit()
        conn.close()

    def adjust_stock(self,product_id, change, movement_type, user="Admin", comment=""):
        """
        Ajuste la quantité d'un produit.
        change : entier positif ou négatif
        movement_type : 'Entrée', 'Sortie', 'Correction'
        """
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()

        # Récupérer ancienne quantité
        cur.execute("SELECT quantity FROM products WHERE ref=?", (product_id,))
        old_qty = cur.fetchone()[0]
        new_qty = old_qty + change

        # Mise à jour de la quantité
        cur.execute("UPDATE products SET quantity=? WHERE ref=?", (new_qty, product_id))
        conn.commit()
        conn.close()

        
    def total_stock_value(self):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()
        cur.execute("SELECT SUM(quantity * price) FROM products")
        result = cur.fetchone()[0] or 0
        conn.close()
        return result

    def products_in_low_stock(self):
        conn = self.get_connection()
        if conn is None:
            return False
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products WHERE quantity <= alert_min")
        result = cur.fetchone()[0]
        conn.close()
        return result
