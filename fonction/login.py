
__version__ = "1.2.0111"
authors = "ZONGO Soumaïla"
email = "soumailazongo04@gmail.com"
# -*- coding: utf-8 -*-
################################################################################
# # auteur: ZONGO Soumaïla
# Tel: +226 54267778 / 70925613
################################################################################

from interface.icon_rc import *
from PySide6.QtCore import QLoggingCategory, Signal

QLoggingCategory.setFilterRules("qt.gui.icc=false")
from PySide6.QtGui import QAction
from pathlib import Path
import os

import sqlite3 as sq
from PySide6.QtWidgets import (QMessageBox, QDialog)
from fonction.module import *
# from interface.acceuil_ui import Ui_acceuil
from fonction.widzar import ResetPasswordDialog
class login(QDialog):
    # Define a signal that will be emitted when login is successful.
    # It passes the username as a string.
    login_successful = Signal(str)

    def __init__(self,dbfolder) -> None:
        super().__init__()
        self.ui = Ui_acceuil()
        self.ui.setupUi(self)
       
        self.dbfolder = dbfolder
        self.user = None
        self.cal = cal()
        self.ui.adm.clicked.connect(self.login_user)
        self.ui.modifier.clicked.connect(self.mot_de_passe_oublie)
    def login_user(self):
        """Vérifie les informations de connexion."""
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            return QMessageBox.warning(self, "Erreur", "Impossible de se connecter à la base de données.")
        cursor = conn.cursor()
        username = self.ui.lineEdit_25.text()
        password = self.ui.lineEdit_26.text()

        cursor.execute("SELECT paswrd,nom FROM login WHERE nom=?", (username,))
        result = cursor.fetchone()

        if result:
            
            hashed_password = result[0]
    
            # Assurez-vous d'avoir la fonction check_password disponible
            if check_password(password, hashed_password):
                
                # If login is successful, emit the signal and close the login window
                QMessageBox.information(self, "Succès", "Connexion réussie !")
                self.login_successful.emit(username)
                self.user = result[1]
                self.accept()  # Use accept() to close the dialog with a success code
                
            else:
                QMessageBox.warning(self, "Échec", "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            QMessageBox.warning(self, "Échec", "Nom d'utilisateur ou mot de passe incorrect.")
    
    def mot_de_passe_oublie(self):
        """Gère le processus de réinitialisation du mot de passe oublié."""
        dialog = ResetPasswordDialog(self.dbfolder)
        dialog.exec()