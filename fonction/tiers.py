import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox,QHeaderView,QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from fonction.methode import cal

class TiersWidget(QDialog):
    def __init__(self, dbfolder: str, mode=''):
        super().__init__()
        self.dbfolder = dbfolder
        self.mode = mode  # "clients" ou "fournisseurs"
        self.cal = cal()
        self.setWindowIcon(QIcon(':/icon/icone.png'))
        self.setWindowTitle(f"Gestion des {self.mode.capitalize()}")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)

        # --- Filtres et saisie ---
        topbar = QHBoxLayout()
        self.nom_input = QLineEdit(); self.nom_input.setPlaceholderText("Nom")
        self.tel_input = QLineEdit(); self.tel_input.setPlaceholderText("Téléphone")
        self.adr_input = QLineEdit(); self.adr_input.setPlaceholderText("Ville")
        self.email_input = QLineEdit(); self.email_input.setPlaceholderText("Adresse")
        bar_btn= QHBoxLayout()
        btn_add = QPushButton("Ajouter/Modifier")
        btn_del = QPushButton("Supprimer")
        btn_hist = QPushButton("Voir Historique")



        topbar.addWidget(QLabel("Nom:"),2); topbar.addWidget(self.nom_input)
        topbar.addWidget(QLabel("Téléphone:")); topbar.addWidget(self.tel_input)
        topbar.addWidget(QLabel("Ville:")); topbar.addWidget(self.adr_input)
        topbar.addWidget(QLabel("Adresse:")); topbar.addWidget(self.email_input)
        topbar.addWidget(btn_add); bar_btn.addWidget(btn_del); bar_btn.addWidget(btn_hist)
        layout.addLayout(topbar)
        layout.addLayout(bar_btn)

        # --- Tableau des tiers ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom & Prénom", "Téléphone", "Ville", "Adresse", "Solde"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)

        # Connexions
        btn_add.clicked.connect(self.save_tier)
        btn_del.clicked.connect(self.delete_tier)
        btn_hist.clicked.connect(self.show_history)
        self.table.itemSelectionChanged.connect(self.fill_form)

        # Charger au démarrage
        self.load_data()

    def connect(self):
        return sqlite3.connect(self.dbfolder)

    def load_data(self):
        """Charge la liste des tiers avec calcul du solde."""
        self.table.setRowCount(0)
        conn = self.connect(); cur = conn.cursor()
        cur.execute(f"SELECT id,nom,cont,ville,adr FROM client WHERE type =?",(self.mode,))
        rows = cur.fetchall()
        
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
            # Calcul du solde pour chaque client/fournisseur
            id_tier = row[0]
            solde = self.calculer_solde(conn, id_tier)
            self.table.setItem(r, 5, QTableWidgetItem(str(round(solde, 2))))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.resizeColumnsToContents()

        conn.close()

    def calculer_solde(self, conn, id_tier: int) -> float:
        """Calcule le solde d’un client ou fournisseur selon les pièces."""
        cur = conn.cursor()

        if self.mode == "Client":
            # Total factures client
            cur.execute("SELECT IFNULL(SUM(mnt_ttc),0) FROM infov WHERE client=?", (id_tier,))
            total_factures = cur.fetchone()[0] or 0

            # Total paiements reçus
            cur.execute("SELECT IFNULL(SUM(payer),0) FROM infov WHERE client=?", (id_tier,))
            total_paye = cur.fetchone()[0] or 0

            return total_factures - total_paye  # ce que le client doit

        elif self.mode == "Fournisseur":
            # Total achats fournisseur
            cur.execute("SELECT IFNULL(SUM(montant),0) FROM info WHERE id_fr=?", (id_tier,))
            total_achats = cur.fetchone()[0] or 0

            # Total paiements effectués
            cur.execute("SELECT IFNULL(SUM(payé),0) FROM info WHERE id_fr=?", (id_tier,))
            total_paye = cur.fetchone()[0] or 0

            return total_achats - total_paye  # ce que tu dois au fournisseur

        return 0.0

    def save_tier(self):
        nom = self.nom_input.text().strip()
        tel = self.tel_input.text().strip()
        adr = self.adr_input.text().strip()
        email = self.email_input.text().strip()
        refe = self.cal.random_client()

        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return

        conn = self.connect(); cur = conn.cursor()

        # Vérifie si un ID est sélectionné
        selected = self.table.currentRow()
        if selected >= 0:
            id_val = self.table.item(selected, 0).text()
            cur.execute(f"UPDATE client SET nom=?, cont=?, ville=?, adr=? WHERE id=?",
                        (nom, tel, adr, email, id_val))
        else:
            cur.execute(f"INSERT INTO client(nom, cont, ville, adr, type,id) VALUES(?,?,?,?,?,?)",
                        (nom, tel, adr, email,self.mode,refe))
        conn.commit(); conn.close()
        self.load_data()

    def delete_tier(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un enregistrement à supprimer.")
            return
        id_val = self.table.item(selected, 0).text()
        conn = self.connect(); cur = conn.cursor()
        cur.execute(f"DELETE FROM client WHERE id=?", (id_val,))
        msg = QMessageBox(self)
        msg.setWindowTitle("SUPPRESSION")
        msg.setText(f"Êtes vous sûr de vouloir supprimer cet {self.mode.lower()} ?")
        btn_yes = msg.addButton("Oui",QMessageBox.ButtonRole.YesRole)
        btn_n = msg.addButton("Non",QMessageBox.ButtonRole.NoRole)
        msg.exec()
        if msg.clickedButton() == btn_yes:
            conn.commit()
        elif msg.clickedButton() == btn_n:
            conn.rollback() 
        
        self.load_data()

    def fill_form(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.nom_input.setText(self.table.item(selected, 1).text())
            self.tel_input.setText(self.table.item(selected, 2).text())
            self.adr_input.setText(self.table.item(selected, 3).text())
            self.email_input.setText(self.table.item(selected, 4).text())

    
    def show_history(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un enregistrement pour voir son historique.")
            return
        id_val = self.table.item(selected, 0).text()

        conn = self.connect()
        dlg = HistoriqueDialog(conn, id_val, mode=self.mode)
        dlg.exec()
        conn.close()


class HistoriqueDialog(QDialog):
    def __init__(self, conn, id_tier, mode="Client"):
        super().__init__()
        self.setWindowTitle(f"Historique {mode.capitalize()}")
        self.setWindowIcon(QIcon(':/icon/chariot-de-chariot.png'))
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(650,500)
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        layout.addWidget(self.table)

        cur = conn.cursor()
        if mode == "Client":
            cur.execute("""SELECT factu, mnt_ttc, payer, datee, statut, remarque
                           FROM infov WHERE client=? ORDER BY datee DESC""", (id_tier,))
            rows = cur.fetchall()
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(["Facture", "Montant TTC", "Payé", "Date", "Statut", "Remarque"])
        else:
            cur.execute("""SELECT factu, mnt_ttc, payé, datee,statut
                           FROM info WHERE id_fr=? ORDER BY datee DESC""", (id_tier,))
            rows = cur.fetchall()
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["Facture", "Montant", "Payé", "Date","Statut"])

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
    
