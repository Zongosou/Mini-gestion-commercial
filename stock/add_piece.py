from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel,
    QLineEdit, QDateEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox,QApplication,QDoubleSpinBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon, QFont, QColor, QIntValidator, QDoubleValidator
import sqlite3              
from fonction.methode import cal
# Assurez-vous d'avoir la classe DbManager définie ci-dessus et d'autres utilitaires nécessaires.


    # ... autres méthodes (ajouter produit, get_produit_par_id, etc.) seront nécessaires.
class AchatModule(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        if parent:
            # même taille que la fenêtre parente
            screen = QApplication.primaryScreen()
            size = screen.availableGeometry()
            w = int(size.width() * 0.8)
            h = int(size.height() * 0.8)
            self.resize(w, h)
            frame_geo = self.frameGeometry()
            center_point = screen.availableGeometry().center()
            frame_geo.moveCenter(center_point)
            self.move(frame_geo.topLeft())
        self.setWindowTitle("Gestion des Achats et Réception de Stock")
        self.setWindowIcon(QIcon(":/icon/icone.png"))
        
        self.db = db_manager
        self.cal = cal()

        self.current_user = "Utilisateur Test" # À remplacer par le vrai utilisateur

        self.initUI()
        self.get_id_fournisseur()
      
    def initUI(self):
        main_layout = QVBoxLayout(self)

        # 1. Formulaire de la Facture (Entête)
        header_group = QGroupBox("Détails de la Facture Fournisseur")
        header_layout = QFormLayout(header_group)
        
        self.ref_input = QLineEdit()
        self.date_input = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.id_fournisseur_input = QComboBox(placeholderText="ID du fournisseur")
        self.id_fournisseur_input.activated.connect(self.get_info_fournisseur)

        self.type_facture_input = QLineEdit(placeholderText="Type de la facture")
        self.fournisseur_input = QLineEdit(placeholderText="Nom du fournisseur")
        self.statut_combo = QComboBox()
        self.statut_combo.addItems(["En attente de paiement", "Payée"])
        header_layout.addRow("Type de Facture:", self.type_facture_input)
        header_layout.addRow("Référence Facture:", self.ref_input)
        header_layout.addRow("Date de Réception:", self.date_input)
        header_layout.addRow("ID Fournisseur:", self.id_fournisseur_input)
        header_layout.addRow("Fournisseur:", self.fournisseur_input)
        header_layout.addRow("Statut:", self.statut_combo)
        
        main_layout.addWidget(header_group)
        
        # 2. Tableau des Lignes de Produit
        lines_group = QGroupBox("Produits Achetés et Reçus (Mise à jour du Stock)")
        lines_layout = QVBoxLayout(lines_group)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Produit", "Quantité Achetée", "Prix Achat", "Total"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.AnyKeyPressed)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lines_layout.addWidget(self.table)
        
        # Bouton Ajouter Ligne
        add_line_btn = QPushButton("Ajouter un Produit à la Facture")
        add_line_btn.setIcon(QIcon(":/icon/plus.png"))
        add_line_btn.setToolTip("Ajouter une nouvelle ligne de produit à la facture.")
        add_line_btn.setObjectName("SecondaryButton")
        
        add_line_btn.clicked.connect(self.add_product_line)
        lines_layout.addWidget(add_line_btn)
        main_layout.addWidget(lines_group)
        
        # 3. Boutons d'Action
        action_layout = QHBoxLayout()
        self.total_label = QLabel("Montant Total Facture (Calculé): 0.00 €")
        save_btn = QPushButton("Valider la Facture et Mettre le Stock à Jour")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setIcon(QIcon(":/icon/save.png"))
        save_btn.setToolTip("Enregistre la facture et met à jour les quantités en stock.")
        save_btn.clicked.connect(self.save_and_update_stock)

        self.input_payed = QLineEdit()
        self.input_payed.setValidator(QDoubleValidator(0.00, 9999999999.99, 2))
        self.input_payed.setPlaceholderText("Montant Payé chez le Fournisseur")
        self.id_fournisseur_input.currentTextChanged.connect(self.get_info_fournisseur)
        action_layout.addWidget(self.total_label)
        action_layout.addStretch()
        action_layout.addWidget(save_btn)
        main_layout.addLayout(action_layout)
    
    def get_produit_par_id(self, produit_id):
        """Récupère les informations d'un produit par son ID."""
        conn=self.cal.connect_to_db(self.db)
        if conn:
            cursor=conn.cursor()
            query="SELECT name, quantity, price FROM products WHERE ref=?"
            cursor.execute(query,(produit_id,))
            result=cursor.fetchone()
            conn.close()
            if result:
                nom, quantite, price = result
                return {"id": produit_id, "nom": nom, "quantite": quantite, "price": price}
        return None
    
    def load_all_products(self):
        """Charge tous les produits disponibles dans le stock."""
        products = []
        conn=self.cal.connect_to_db(self.db)
        if conn:
            cursor=conn.cursor()
            query="SELECT ref, name, price FROM products"
            cursor.execute(query)
            result=cursor.fetchall()
            for row in result:
                pid, nom, price = row
                products.append({"id": pid, "nom": nom, "price": price})
            conn.close()
        return products

    def get_info_fournisseur(self):
        """Récupère les informations du fournisseur sélectionné."""
        conn=self.cal.connect_to_db(self.db)
        if conn:
            id_fournisseur = self.id_fournisseur_input.currentData()
            cursor=conn.cursor()
            query="SELECT nom FROM client WHERE id=? AND type='Fournisseur'"
            cursor.execute(query,(id_fournisseur,))
            result=cursor.fetchone()
            if result:
                nom= result[0]
                self.fournisseur_input.setText(nom)
            conn.close()

    # ------------------ LOGIQUE DE L'UI ------------------
    def get_id_fournisseur(self):
        conn=self.cal.connect_to_db(self.db)
        if conn:
            cursor=conn.cursor()
            query="SELECT id,nom FROM client WHERE type='Fournisseur'"
            cursor.execute(query)
            result=cursor.fetchall()
            for did, nom in result:
                self.id_fournisseur_input.addItem(f"{did} {nom}", userData=did)
            conn.close()

        """Récupère l'ID du fournisseur sélectionné."""
        return self.id_fournisseur_input.currentText()
    def add_product_line(self):
        """Ajoute une ligne de produit avec un ComboBox de sélection."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.products = self.load_all_products()
       
        # Colonne 0 : Sélection du produit (ComboBox)
        product_combo = QComboBox()
        product_combo.addItem("- Sélectionner un produit -", userData=None)
        for p in self.products:
            # itemData contient l'ID du produit
            product_combo.addItem(f"{p['nom']}", userData=p['id'])
        
        self.table.setCellWidget(row_count, 0, product_combo)
        
        # Colonne 1 : Quantité
        qt_spin = QDoubleSpinBox()
        qt_spin.setMinimum(0)
        qt_spin.setMaximum(9999999.99)
        qt_spin.setValue(1.0)
        self.table.setCellWidget(row_count, 1, qt_spin)
        qt_spin.valueChanged.connect(self.recalculate_totals)

        # Colonne 2 : Prix unitaire
       
        prix_spin = QDoubleSpinBox()
        prix_spin.setMinimum(0)
        prix_spin.setMaximum(9999999999)
        prix_spin.setValue(float(0.00))
        prix_spin.setDecimals(2)
        self.table.setCellWidget(row_count, 2, prix_spin)
        prix_spin.valueChanged.connect(self.recalculate_totals)

        # Colonne 3 : Total Ligne (Non éditable)
        total_item = QTableWidgetItem("0.00")
        total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row_count, 3, total_item)
        
        # Connecter les changements pour le calcul en temps réel
        product_combo.currentIndexChanged.connect(self.recalculate_totals)
    
        
    def recalculate_totals(self):
        """Calcule le total de la ligne et le total général."""
        total_general = 0.0
        
        for row in range(self.table.rowCount()):
            try:
                # Récupérer Quantité et Prix unitaire
                qty_item = self.table.cellWidget(row, 1)
                price_item = self.table.cellWidget(row, 2)
                
                if qty_item and price_item:
                    quantite = float(qty_item.value())
                    prix = float(price_item.value())
                    
                    total_ligne = round(quantite * prix, 2)
                    total_general += total_ligne
                    
                    # Mettre à jour la cellule Total Ligne
                    self.table.item(row, 3).setText(f"{total_ligne:,.2f}".replace(",", " ").replace(".", ","))
                    
            except Exception:
                # Ignorer les erreurs de conversion (texte invalide)
                continue
        
        # Mettre à jour le label du Total Général
        self.total_label.setText(f"Montant Total Facture (Calculé): {total_general:,.2f} €".replace(",", " ").replace(".", ","))


    # ------------------ LOGIQUE MÉTIER ET SAUVEGARDE ------------------

    def save_and_update_stock(self):
        """
        1. Vérifie la validité des données.
        2. Enregistre la facture d'achat.
        3. Met à jour la quantité en stock pour chaque ligne.
        """
        type_facture = self.type_facture_input.text().strip()
        ref = self.ref_input.text().strip()
        date_rec = self.date_input.date().toString("yyyy-MM-dd")
        fournisseur = self.fournisseur_input.text().strip()
        id_fournisseur = self.id_fournisseur_input.currentData()
        statut = self.statut_combo.currentText()
        total_calcule = self._get_calculated_total()
        montant_paye = self.input_payed.text().strip()
        montant_paye = float(montant_paye) if montant_paye else 0.0

        if not ref or not fournisseur or total_calcule <= 0:
            QMessageBox.warning(self, "Erreur de Saisie", "Veuillez remplir la référence, le fournisseur et vous assurer que le total est positif.")
            return

        lignes = self._get_lignes_facture()
        
        if not lignes:
            QMessageBox.warning(self, "Erreur de Saisie", "La facture doit contenir au moins un produit valide.")
            return

        try:
            conn = self.cal.connect_to_db(self.db)
            if conn is None:
                raise Exception("Connexion à la base de données impossible.")
            cursor = conn.cursor()
            # 1. Enregistrer la facture d'achat (Entête)
            montant_reste = total_calcule - montant_paye
            if montant_reste < 0:
                montant_reste = 0.0

            cursor.execute("""
            INSERT INTO info (factu, id_fr, montant, mnt_paye, reste, 
                                       datee, statut, type_piece,  utilisateur)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ref,id_fournisseur, total_calcule, montant_paye, montant_reste, date_rec, statut, type_facture, self.current_user))
            
            facture_id = cursor.lastrowid
            
            # 2. Enregistrer les lignes de facture et Mettre à jour le stock
            for ref,produit_id, prix_achat,quantite, montant_ligne,date_rec,id_fournisseur,type_facture,current_user in lignes:
                
                # a. Enregistrer la Ligne de Facture
                cursor.execute("""
                INSERT INTO hist (fact, code, prix, quantite,montant, tdate,id_four, type_piece,utilisateur)
                VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ref, produit_id, prix_achat, quantite, montant_ligne,date_rec,id_fournisseur,type_facture,current_user))
                
                # b. Mettre à jour le Stock (L'action qui augmente l'inventaire)
                cursor.execute("""SELECT qty FROM stock WHERE id_libelle = ?""", (produit_id,))
                result = cursor.fetchone()
                cursor.execute("""
                    INSERT INTO stock (id_libelle, qty, price)
                    VALUES (?, ?, ?)
                    ON CONFLICT(id_libelle)
                    DO UPDATE SET
                        qty = stock.qty + excluded.qty,
                        price = excluded.price
                """, (produit_id, quantite, prix_achat))

                # if result is None:
                #     # Produit n'existe pas dans le stock, insérer une nouvelle entrée
                #     cursor.execute("""
                #     INSERT INTO stock (id_libelle, qty, price)
                #     VALUES (?, ?, ?)
                #     """, (produit_id, quantite, prix_achat))
                # cursor.execute("""
                # UPDATE stock 
                # SET qty = qty + ?, 
                #     price = ? -- On pourrait aussi calculer un coût moyen ici
                # WHERE id_libelle = ?
                # """, (quantite, prix_achat, produit_id))
            
            conn.commit()
            QMessageBox.information(self, "Succès", f"Facture {ref} enregistrée et stock mis à jour.")
            self.accept() # Fermer la fenêtre
            
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Erreur BD", f"La référence de facture {ref} existe déjà ou une clé est manquante.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Inconnue", f"Une erreur s'est produite lors de la sauvegarde : {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()


    def _get_calculated_total(self) -> float:
        """Récupère le total calculé à partir du label."""
        text = self.total_label.text().split(':')[-1].strip().replace('€', '').replace(' ', '').replace(',', '.')
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _get_lignes_facture(self) -> list:
        """Extrait les données valides des lignes du tableau."""
        lignes = []
        type_facture = self.type_facture_input.text().strip()
        ref = self.ref_input.text().strip()
        date_rec = self.date_input.date().toString("yyyy-MM-dd")
        id_fournisseur = self.id_fournisseur_input.currentData()
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 0)
            qty_item = self.table.cellWidget(row, 1)
            price_item = self.table.cellWidget(row, 2)
            
            if combo is None or qty_item is None or price_item is None:
                continue

            produit_id = combo.currentData()
            
            try:
                quantite = float(qty_item.value())
                prix_achat = float(price_item.value())
                montant_ligne = quantite * prix_achat
                if quantite <= 0 or prix_achat <= 0:
                    continue # Ignorer les lignes avec quantité ou prix non valides
            except ValueError:
                continue # Ligne ignorée si les montants ne sont pas valides
            
            if produit_id is not None and quantite > 0:
                lignes.append((ref,produit_id, prix_achat,(quantite), montant_ligne,date_rec,id_fournisseur,type_facture,self.current_user))
                
        return lignes

    def removeLigne(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)
        self.recalculate_totals()
   