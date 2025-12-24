from datetime import datetime
import os
import sqlite3
import webbrowser
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from PySide6.QtGui import  QIcon
import logging.config
from PySide6.QtWidgets import ( QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QLineEdit,QLabel,
    QComboBox, QDateEdit, QMessageBox, 
    QGroupBox, QFormLayout, QRadioButton,
    
)
from PySide6.QtCore import QDate, Qt,QDir
from PySide6.QtGui import QIcon
from fonction.methode import cal

# --- Configuration du logging (repris de votre caisse.py) ---
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'filename': 'journal_app.log', # Nom du fichier de log pour cette app
            'maxBytes': 10485760, # 10 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
    }
}
logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader('template'))

class NewTresorerieOp(QDialog):
    def __init__(self, db_path, user=None):
        super().__init__()
        self.setWindowTitle("ENREGISTREMENT CAISSE / BANQUE")
        self.setWindowIcon(QIcon(":/icon/icone.png"))
        # Ajustement de la taille de la fenêtre (plus petite car moins de champs)
        self.resize(500, 280)
        self.setMaximumSize(500, 280) 
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        # self.setWindowIcon(QIcon(':/icon/icone.png')) # Commenté car l'icône n'est pas définie ici
        self.db_path = db_path
        self.cal = cal()
        self.charged = self.cal.charger_configuration_paie()
        charge_devise = self.cal.charger_tva_devise(self.db_path)

        # Config par défaut
        self.devise = charge_devise["devise"] if charge_devise else "CFA"
        self.tva = float(charge_devise["tva"]) if charge_devise else 0.0
        self.current_user = user or "Administrateur"
        
        self.initUI()
        self.update_fields_by_operation_type() # Renommé
        
    # ----------------- UI -----------------
    def initUI(self):
        self.setLayout(QVBoxLayout())
        main_layout = self.layout()

        # GroupBox
        new_entry_group = QGroupBox("Nouvelle Opération de Trésorerie")
        new_entry_layout = QVBoxLayout(new_entry_group)
        main_layout.addWidget(new_entry_group)

        form_layout = QFormLayout()

        # Date et Libellé (inchangé)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)

        self.libelle_input = QLineEdit()
        form_layout.addRow("Libellé (Motif):", self.libelle_input)

        # ⭐️ Montant (HT/TTC - Champ unique pour la saisie) ⭐️
        self.montant_input = QLineEdit()
        self.montant_input.setPlaceholderText(f"Montant ({self.devise})")
        form_layout.addRow(f"Montant ({self.devise}):", self.montant_input)
        
        # ⭐️ Taux TVA (Affiché/Caché selon l'opération) ⭐️
        self.taux_tva_combo = QComboBox()
        self.taux_tva_combo.addItem(f"{self.tva}%", self.tva / 100)
        self.taux_tva_combo.addItem("0%", 0.0) # Option TVA 0
        self.tva_label = QLabel("Taux TVA:")
        
        tva_layout = QHBoxLayout()
        tva_layout.addWidget(self.taux_tva_combo)
        tva_layout.addWidget(QLabel("(Seulement pour les dépenses)"), 1)
        
        # On utilise une ligne complète pour pouvoir cacher le label et le combo
        form_layout.addRow(self.tva_label, tva_layout) 

        # ⭐️ Compte de Trésorerie Impliqué ⭐️
        self.compte_tresorerie_combo = QComboBox()
        self.compte_tresorerie_combo.addItem("Caisse", "Caisse")
        self.compte_tresorerie_combo.addItem("Banque", "Banque")
        form_layout.addRow("Compte de Trésorerie:", self.compte_tresorerie_combo)
        
       
        new_entry_layout.addLayout(form_layout)

        # Type opération (simplifié pour la trésorerie)
        type_op_group = QGroupBox("Nature du Flux")
        type_op_layout = QHBoxLayout(type_op_group)

        self.radio_encaissement = QRadioButton("Encaissement (ENTRÉE)")
        self.radio_decaissement = QRadioButton("Décaissement (SORTIE)")
        self.radio_virement_caisse_banque = QRadioButton("Virement Caisse <> Banque")
        
        self.radio_decaissement.setChecked(True) # Dépense est le cas le plus fréquent

        type_op_layout.addWidget(self.radio_encaissement)
        type_op_layout.addWidget(self.radio_decaissement)
        type_op_layout.addWidget(self.radio_virement_caisse_banque)

        new_entry_layout.addWidget(type_op_group)

        # Connexion radio
        self.radio_encaissement.toggled.connect(self.update_fields_by_operation_type)
        self.radio_decaissement.toggled.connect(self.update_fields_by_operation_type)
        self.radio_virement_caisse_banque.toggled.connect(self.update_fields_by_operation_type)

        # Bouton sauvegarde
        save_button = QPushButton("Enregistrer l'Opération de Trésorerie")
        save_button.setObjectName("PrimaryButton") 
        
        new_entry_layout.addWidget(save_button)
        save_button.clicked.connect(self.save_operation)
        
  
    
    def update_fields_by_operation_type(self):
        """Ajuste l'UI selon la nature du flux (Caisse/Banque, TVA)."""
        
        is_virement = self.radio_virement_caisse_banque.isChecked()
        is_depense = self.radio_decaissement.isChecked()

        # Gérer la visibilité du champ TVA
        if is_depense:
            self.tva_label.show()
            self.taux_tva_combo.show()
            self.montant_input.setPlaceholderText(f"Montant HT si TVA, ou TTC")
            self.montant_input.setText("") # Vider pour forcer la nouvelle saisie

        else:
            # Encaissement ou Virement : le montant saisi est TTC/Global
            self.tva_label.hide()
            self.taux_tva_combo.hide()
            self.montant_input.setPlaceholderText(f"Montant TTC / Global")
            
        # Gérer le sélecteur Caisse/Banque
        if is_virement:
            # Pour un virement, on a besoin de savoir lequel est la source (Caisse -> Banque ou vice-versa)
            # On laisse le sélecteur pour choisir le compte DE DÉPART (SORTIE)
            self.compte_tresorerie_combo.show()
        else:
            # Encaissement ou Décaissement : on choisit juste le compte affecté
            self.compte_tresorerie_combo.show()
            
   
    # ----------------- SAUVEGARDE SIMPLIFIÉE -----------------
    def save_operation(self):
        try:
            date_operation = self.date_edit.date().toPython()
            libelle = self.libelle_input.text().strip()
            montant_brut = float(self.montant_input.text().replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un montant valide (chiffres).")
            return
        
        if not libelle:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un libellé.")
            return

        type_op_flux = ""
        compte_tresorerie_selectionne = self.compte_tresorerie_combo.currentData()
        
        # --- Gestion de la TVA (uniquement si le champ est visible, donc pour les dépenses/Décaissement) ---
        montant_ttc = montant_brut
        montant_tva = 0.0
        
        if self.radio_decaissement.isChecked() and self.taux_tva_combo.isVisible():
            # Si c'est une dépense et que la TVA est affichée, montant_brut est considéré HT
            taux_tva = float(self.taux_tva_combo.currentData())
            montant_tva = round(montant_brut * taux_tva, 2)
            montant_ttc = round(montant_brut + montant_tva, 2)
            # Note: Si vous voulez que la TVA soit un champ distinct pour les dépenses,
            # il faudrait adapter l'UI pour avoir Montant HT + TVA + TTC affiché.

        # --- Logique de Flux (ENTRÉE / SORTIE) ---

        if self.radio_encaissement.isChecked():
            # Encaissement = ENTRÉE dans le compte sélectionné
            self.insert_tresorerie(date_operation, libelle, montant_ttc, "ENTREE", compte_tresorerie_selectionne)
            QMessageBox.information(self, "Succès", f"Encaissement enregistré : {montant_ttc} {self.devise} dans {compte_tresorerie_selectionne}.")

        elif self.radio_decaissement.isChecked():
            # Décaissement = SORTIE du compte sélectionné
            self.insert_tresorerie(date_operation, libelle, montant_ttc, "SORTIE", compte_tresorerie_selectionne)
            QMessageBox.information(self, "Succès", f"Décaissement enregistré : {montant_ttc} {self.devise} de {compte_tresorerie_selectionne}.")
            
        elif self.radio_virement_caisse_banque.isChecked():
            # Virement : Une sortie d'un compte ET une entrée dans l'autre
            
            compte_destination = "Caisse" if compte_tresorerie_selectionne == "Banque" else "Banque"
            
            # 1. SORTIE du compte sélectionné
            self.insert_tresorerie(date_operation, f"Virement vers {compte_destination} - {libelle}", montant_brut, "SORTIE", compte_tresorerie_selectionne)
            
            # 2. ENTRÉE dans l'autre compte
            self.insert_tresorerie(date_operation, f"Virement depuis {compte_tresorerie_selectionne} - {libelle}", montant_brut, "ENTREE", compte_destination)
            
            QMessageBox.information(self, "Succès", f"Virement enregistré : {montant_brut} {self.devise} de {compte_tresorerie_selectionne} vers {compte_destination}.")
            
        else:
             QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un type d'opération.")
             return
             
        self.clear_form() # Vider le formulaire après succès


    # ----------------- DB (Adapté) -----------------
    def insert_tresorerie(self, date_op, libelle, montant, type_op, compte):
        """
        Enregistre l'opération de trésorerie simple.
        
        type_op doit être 'ENTREE' ou 'SORTIE'.
        compte doit être 'Caisse' ou 'Banque'.
        """
        conn = self._get_db_connection() # Utilisation d'une fonction d'aide
        if conn is None: return False
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO tresorerie (date_operation, libelle, montant, type, compte, reference, utilisateur)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date_op.strftime("%Y-%m-%d"), libelle, montant, type_op, compte, self.cal.random_recette(), self.current_user))
            conn.commit()
            return True
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur BD", f"Erreur trésorerie : {e}")
            return False
        finally:
            conn.close()

    def _get_db_connection(self):
        """Fonction d'aide pour se connecter à la DB et gérer les erreurs."""
        try:
             # Utiliser la méthode de connexion de 'cal' si elle est fiable
            conn = sqlite3.connect(self.db_path) 
            return conn
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur BD", f"Connexion échouée: {e}")
            return None

    def clear_form(self):
        self.date_edit.setDate(QDate.currentDate())
        self.libelle_input.clear()
        self.montant_input.clear()
        self.radio_decaissement.setChecked(True)
        self.update_fields_by_operation_type() # Renommé