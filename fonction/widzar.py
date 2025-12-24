import re
import secrets
import sqlite3
from PySide6.QtWidgets import (
     QDialog, QTabWidget, QWidget,
    QVBoxLayout, QFormLayout,  QLineEdit, QPushButton,
    QDateEdit, QRadioButton, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QDoubleSpinBox
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QIcon


from fonction.methode import cal
from fonction.module import hash_password
import os

CONFIG_FOLDER = "config"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
file_auth = "config/id_servers.json"
class SetupWizardTabs(QDialog):
    def __init__(self, db_path=None):
        super().__init__()
        self.setWindowTitle("Configuration initiale")
        self.setWindowIcon(QIcon(":/icon/icone.png"))
        self.resize(600, 400)
        self.db_path = db_path
        self.cal = cal()
        # if self.si_existe():
        #     self.close()
        #     return
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # === Onglets ===
        self.tab_entreprise = QWidget()
        self.tabs.addTab(self.tab_entreprise, "Entreprise")
        self._init_onglet_entreprise()

        self.tab_exercice = QWidget()
        self.tabs.addTab(self.tab_exercice, "Exercice & Dépôts")
        self._init_onglet_exercice()

        self.tab_users = QWidget()
        self.tabs.addTab(self.tab_users, "Utilisateurs")
        self._init_onglet_users()

        # Bouton final et Bouton d'affichage
        Box_Hor = QHBoxLayout()
        self.btn_save = QPushButton("Enregistrer la configuration")
        self.btn_load = QPushButton("Afficher les données")
        self.btn_save.setIcon(QIcon(":/icon/administration.png"))
        self.btn_save.clicked.connect(self.save_all)
        self.btn_load.clicked.connect(self._ini_onglet_affiche)
        Box_Hor.addWidget(self.btn_save)
        Box_Hor.addWidget(self.btn_load)
        layout.addLayout(Box_Hor)
        self.affiche_config()
    # === Onglet Entreprise ===
    def _init_onglet_entreprise(self):
        form = QFormLayout(self.tab_entreprise)
        self.nom_entreprise = QLineEdit()
        self.tel1 = QLineEdit()
        self.tel2 = QLineEdit()
        self.responsable = QLineEdit()
        self.adresse = QLineEdit();self.adresse.setPlaceholderText("Nom du secteur ou le Numéro")
        self.ville = QLineEdit()
        self.ifu = QLineEdit();self.ifu.setPlaceholderText("IFU-CNSS-RCCM")
        self.autre = QLineEdit();self.autre.setPlaceholderText("Email, Poste, ou autre")
        self.details = QLineEdit();self.details.setPlaceholderText("Information sur votre service")
        
        form.addRow("Nom entreprise:", self.nom_entreprise)
        form.addRow("Détails:",self.details)
        form.addRow("Téléphone:", self.tel1)
        form.addRow("WhatsApp:", self.tel2)
        form.addRow("Responsable:", self.responsable)
        form.addRow("Adresse:", self.adresse)
        form.addRow("Ville:", self.ville)
        form.addRow("IFU:", self.ifu)
        form.addRow("Autres infos:", self.autre)
        
    # === Onglet Exercice ===
    def _init_onglet_exercice(self):
        main_layout = QVBoxLayout(self.tab_exercice)
        form = QFormLayout()

        self.date_debut = QDateEdit(QDate.currentDate())
        self.date_fin = QDateEdit(QDate.currentDate().addYears(1))
        self.devise = QLineEdit("CFA")
        self.tva = QDoubleSpinBox()
        self.tva.setValue(18.0)

        self.radio_simple = QRadioButton("Simple dépôt")
        self.radio_multi = QRadioButton("Multi-dépôts")
        self.radio_simple.setChecked(True)
        self.radio_simple.toggled.connect(self.toggle_depot_mode)

        depot_layout = QHBoxLayout()
        depot_layout.addWidget(self.radio_simple)
        depot_layout.addWidget(self.radio_multi)

        form.addRow("Début exercice:", self.date_debut)
        form.addRow("Fin exercice:", self.date_fin)
        form.addRow("Devise:", self.devise)
        form.addRow("TVA (%):", self.tva)
        form.addRow("Mode dépôt:", depot_layout)

        main_layout.addLayout(form)

        # Table pour multi-dépôts
        self.table_depots = QTableWidget(0, 2)
        self.table_depots.setHorizontalHeaderLabels(["Nom dépôt", "Localisation"])
        self.btn_add_depot = QPushButton("➕ Ajouter dépôt")
        self.btn_add_depot.clicked.connect(self.add_depot)

        main_layout.addWidget(self.table_depots)
        main_layout.addWidget(self.btn_add_depot)

        # Par défaut désactivé (car simple dépôt sélectionné)
        self.table_depots.setDisabled(True)
        self.btn_add_depot.setDisabled(True)
    # onglet pour afficher tous les informations
    def _ini_onglet_affiche(self):
        self.curentTab = self.tabs.currentIndex()
        conn = self.cal.connect_to_db(self.db_path)
        if conn is None:
            return
        cur = conn.cursor()
        if self.curentTab == 0:
            sqls = '''SELECT * from infoentre'''
            cur.execute(sqls)
            resu = cur.fetchone()
            if resu:
                nom_entreprise = resu[0]  
                tele = resu[1]
                tele1 = resu[2]
                detail = resu[3]
                nom1 = resu[4]
                adr = resu[5]
                ville = resu[6]
                ifu = resu[7]
                autre = resu[8]
           
                self.nom_entreprise.setText(nom_entreprise)
                self.tel1.setText(tele)
                self.tel2.setText(tele1)
                self.autre.setText(autre)
                self.responsable.setText(nom1)
                self.adresse.setText(adr)
                self.ville.setText(ville)
                self.ifu.setText(ifu)
                self.details.setText(detail)
                conn.close()
        if self.curentTab == 1:
            sqls = '''SELECT date_debut,date_fin,devise,tva from config'''
            cur.execute(sqls)
            resu = cur.fetchone()
            if resu:
                date_debu = resu[0]  
                date_fin = resu[1]
                date_debu = QDate.fromString(resu[0], "yyyy-MM-dd")
                date_fin = QDate.fromString(resu[1], "yyyy-MM-dd")
                devise=resu[2]
                tva=resu[3]
                self.date_debut.setDate(date_debu)
                self.date_fin.setDate(date_fin)
                self.devise.setText(str(devise))
                self.tva.setValue(float(tva))
            conn.close()
        elif self.curentTab == 2:
            sqls = '''SELECT nom,paswrd,email,id_int from login'''
            cur.execute(sqls)
            resu = cur.fetchall()
            if resu:
                for row_data in resu:
                    row = self.table_users.rowCount()
                    self.table_users.insertRow(row)
                    self.table_users.setItem(row, 0, QTableWidgetItem(str(row_data[0])))
                    self.table_users.setItem(row, 1, QTableWidgetItem(str(row_data[1])))
                    self.table_users.setItem(row, 2, QTableWidgetItem(str(row_data[2])))
                    self.table_users.setItem(row, 3, QTableWidgetItem(str(row_data[3])))
            conn.close()
        
        

    def toggle_depot_mode(self):
        """Active/désactive la table selon le mode"""
        is_multi = self.radio_multi.isChecked()
        self.table_depots.setEnabled(is_multi)
        self.btn_add_depot.setEnabled(is_multi)

    def add_depot(self):
        # Le dernier numero
        conn = self.cal.connect_to_db(self.db_path)
        if conn is None:
            return []
        cur = conn.cursor()
        row = cur.execute("SELECT COUNT(*) FROM depots")
        row = row.lastrowid
        
        """Ajoute une ligne de dépôt"""
        row = self.table_depots.rowCount()
        self.table_depots.insertRow(row)
        self.table_depots.setItem(row, 0, QTableWidgetItem(f"Dépôt {row+1}"))
        self.table_depots.setItem(row, 1, QTableWidgetItem(f"{self.ville.text().strip()}"))

    # === Onglet Utilisateurs ===
    def _init_onglet_users(self):
        layout = QVBoxLayout(self.tab_users)
        box_h = QHBoxLayout()
        self.user_name = QLineEdit()
        self.user_pass = QLineEdit()
        
        self.user_email = QLineEdit()
        self.user_email.setPlaceholderText("Email utilisateur")
        self.user_name.setPlaceholderText("Nom utilisateur")
        self.user_pass.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("Nom utilisateur:", self.user_name)
        form.addRow("Mot de passe:", self.user_pass)
        form.addRow("Email utilisateur:", self.user_email)
        
        self.btn_add_user = QPushButton("☺️Ajouter utilisateur")
        self.btn_add_user.clicked.connect(self.add_user)
        box_h.addWidget(self.btn_add_user)
        self.table_users = QTableWidget(0, 3)
        self.table_users.setHorizontalHeaderLabels(["Utilisateur", "Mot de passe", "Email"])
        layout.addLayout(form)
        layout.addWidget(self.btn_add_user)
        layout.addWidget(self.table_users)

    def add_user(self):
        name = self.user_name.text().strip()
        pwd = self.user_pass.text().strip()
       
        if not name or not pwd:
            QMessageBox.warning(self, "Erreur", "Nom ou mot de passe vide")
            return
        row = self.table_users.rowCount()
        self.table_users.insertRow(row)
        self.table_users.setItem(row, 0, QTableWidgetItem(name))
        self.table_users.setItem(row, 1, QTableWidgetItem(pwd))
        self.table_users.setItem(row, 2, QTableWidgetItem(self.user_email.text().strip()))
        
        self.user_name.clear()
        self.user_pass.clear()
        self.user_email.clear()
        
    def verifie_mot(self,mot):
        if len(mot) < 4:
            return False
        symb = re.compile(r'[\W_]')
        chif = re.compile(r'\d')
        Maj = re.compile(r'[A-z]')
        minis = re.compile(r'[a-z]')
        if (symb.search(mot) and chif.search(mot) and Maj.search(mot) and minis.search(mot)):
            return True
        else:
            return False
    
    import secrets

    def generate_recovery_code(self):
        return secrets.token_hex(8)  # Exemple : 'a3f9c2d1b4e5f678'

    # === Sauvegarde en BD ===
    def save_all(self):
        try:
            self.curentTab = self.tabs.currentIndex()
            conn = self.cal.connect_to_db(self.db_path)
            if conn is None:
                return
            cur = conn.cursor()

            # 1) Enregistrer entreprise
            if self.curentTab == 0:
                cur.execute("SELECT COUNT(*) FROM infoentre")
                result = cur.fetchone()[0]
                if result > 0:
                    QMessageBox.warning(self,"Restriction","Les informations de l'entreprise sont déjà enregistrée." "Vous ne pouvez pas en ajouter une nouvelle.")
                    conn.close()
                    return
                cur.execute("""
                    INSERT INTO infoentre (nom, tele, tele1, detail, nom1, adr, ville, ifu, autre)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.cal.nom_upper(self.nom_entreprise.text()), self.tel1.text(), self.tel2.text(),
                    self.autre.text(),self.cal.nom_upper(self.responsable.text()) ,
                    self.adresse.text(), self.ville.text(),
                    self.ifu.text(), self.autre.text()
                ))

            # 2) Enregistrer exercice + mode
            elif self.curentTab == 1:
                cur.execute("SELECT COUNT(*) FROM config")
                result = cur.fetchone()[0]
                mode = "Simple dépôt" if self.radio_simple.isChecked() else "Multi-dépôts"
                if result > 0:
                    cur.execute("UPDATE config SET mode_depot=?",[mode])
                    for i  in range(self.table_depots.rowCount()):
                            nom = self.table_depots.item(i,0)
                            if nom is None:
                                return 
                            nom = nom.text()
                            lo = self.table_depots.item(i,1)
                            if lo is None:
                                return 
                            loc = lo.text()
                            cur.execute("INSERT INTO depots (nom,adresse) VALUES (?,?)",(nom,loc)) 
                else:

                    # mode = "Simple dépôt" if self.radio_simple.isChecked() else "Multi-dépôts"
                    cur.execute("""
                        INSERT INTO config (date_debut, date_fin, devise, tva, mode_depot)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        self.date_debut.date().toString("yyyy-MM-dd"),
                        self.date_fin.date().toString("yyyy-MM-dd"),
                        self.devise.text(), self.tva.value(), mode
                    ))
                    if mode == "Simple dépôt":
                        cur.execute("INSERT INTO depots (nom,adresse,principal) VALUES (?,?,?)",(f"Dépôt_{self.ville.text()}",f"{self.ville.text()}",1))
                        QMessageBox.information(self,"Gestion des dépôts",f"Vous êtes en mode simple dépôt. Un dépôt par défaut nommé Dépôt_{self.ville.text()} sera créé automatiquement")
                    else:
                        for i  in range(self.table_depots.rowCount()):
                            nom = self.table_depots.item(i,0)
                            if nom is None:
                                return 
                            nom = nom.text()
                            lo = self.table_depots.item(i,1)
                            if lo is None:
                                return 
                            loc = lo.text()
                            cur.execute("INSERT INTO depots (nom,adresse) VALUES (?,?)",(nom,loc))
                    
            # 3) Enregistrer utilisateurs
            else:
                for i in range(self.table_users.rowCount()):
                    user = self.table_users.item(i, 0)
                    if user is None:
                        return
                    user_txt = user.text()
                    pwd = self.table_users.item(i, 1)
                    if pwd is None:
                        return
                    pwd_txt = pwd.text()
                    mot_ = hash_password(pwd_txt)
                    
                    email = self.table_users.item(i, 2)
                    if email is None:
                        return
                    email_txt = email.text()

                    
                    recovery_code = self.generate_recovery_code()
                    cur.execute("INSERT INTO login (nom, paswrd,email,recovery_code) VALUES (?,? , ?, ?)", (user_txt, mot_,email_txt, recovery_code))
                    # Sauvegarde sur Google Drive
                    # Sauvegarde du mot de passe dans Google Drive
                    QMessageBox.information(self, "Utilisateur ajouté",
                    f"Utilisateur {user_txt} créé.\nCode de secours : {recovery_code}\n⚠️ Conservez-le précieusement.")
    
                    
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Configuration enregistrée ✅")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer : {e}")
            self.close()    
   
    def affiche_config(self):
        """Charge la configuration depuis un fichier JSON."""
        
        try:
            conn = cal.connect_to_db(self.db_path)
            if conn is None:
                return
            cur = conn.cursor()
            sqls = '''SELECT date_debut,date_fin,devise,tva from config'''
            cur.execute(sqls)
            resu = cur.fetchone()
            if resu:
                date_debu = resu[0]  
                date_fin = resu[1]
                date_debu = QDate.fromString(resu[0], "yyyy-MM-dd")
                date_fin = QDate.fromString(resu[1], "yyyy-MM-dd")
                devise=resu[2]
                tva=resu[3]
                self.date_debut.setDate(date_debu)
                self.date_fin.setDate(date_fin)
                self.devise.setText(str(devise))
                self.tva.setValue(float(tva))
                
        except FileNotFoundError:
            pass

# === Boîte de dialogue de réinitialisation du mot de passe ===
class ResetPasswordDialog(QDialog):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle("Réinitialisation du mot de passe")
        self.resize(300, 200)
        self.setWindowIcon(QIcon(":/icon/parametre-dutilisateur.png"))
        layout = QVBoxLayout(self)

        self.user = QLineEdit(); self.user.setPlaceholderText("Nom utilisateur ou email")
        self.code = QLineEdit(); self.code.setPlaceholderText("Code de secours")
        self.newpwd = QLineEdit(); self.newpwd.setPlaceholderText("Nouveau mot de passe"); self.newpwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm = QLineEdit(); self.confirm.setPlaceholderText("Confirmer mot de passe"); self.confirm.setEchoMode(QLineEdit.EchoMode.Password)

        btn = QPushButton("👽Réinitialiser")
        
        btn.clicked.connect(self.reset_password)

        for w in [self.user, self.code, self.newpwd, self.confirm, btn]:
            layout.addWidget(w)

    def reset_password(self):
        if self.newpwd.text() != self.confirm.text():
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas")
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT uid, recovery_code FROM login WHERE nom=? OR email=?", (self.user.text(), self.user.text()))
        row = cur.fetchone()
        if not row:
            QMessageBox.warning(self, "Erreur", "😥Utilisateur introuvable")
            return
        if row[1] != self.code.text():
            QMessageBox.warning(self, "Erreur", "😥Code de secours invalide")
            return

        mot_hache = hash_password(self.newpwd.text())
        cur.execute("UPDATE login SET paswrd=? WHERE uid=?", (mot_hache, row[0]))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Succès", "Mot de passe réinitialisé ✅")
        self.accept()
