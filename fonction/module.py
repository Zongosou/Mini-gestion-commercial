# auteur: zongo soumaïla
# Tel: +226 54267778 / 70925613
# -*- coding: utf-8 -*-
from datetime import datetime
import json
from pathlib import Path
import re, os

from PySide6.QtGui import (QPixmap,QRegularExpressionValidator)
from PySide6.QtCore import Qt,QDate,QRegularExpression
from PySide6.QtWidgets import (QTableWidgetItem, QMessageBox, QDialog,QFileDialog)
import bcrypt
try:
    from num2words import num2words
except:
    pass
# from interface.parametre_ui import Ui_inscription
from PIL import Image
from .methode import cal
import logging

def save_log():
    bureau = Path.home() / "Desktop"
    dossier = bureau / "FichierErreur"
    dossier.mkdir(exist_ok =True)
    return dossier

dossier = save_log()
def config(dossier):
    msg = "%(asctime)s - %(levelname)s -%(message)s"
    date_f = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(filename=dossier / 'erreur.log',level=logging.ERROR,format=msg,datefmt=date_f)     
config(dossier)  
   
def hash_password(password):
    """Hache le mot de passe avec un sel."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
def check_password(input_password, stored_hashed_password):
    """Vérifie le mot de passe saisi par rapport au hash stocké."""
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hashed_password)
CONFIG_FOLDER = 'config'


#<===================== classe utilisateur, client, fournisseur et login ==============>
log = logging.getLogger(__name__) 
class Personal(QDialog):
    def __init__(self,dbfolder = None) -> None:
        super().__init__()
        self.ui = Ui_inscription()
        self.ui.setupUi(self)
        self.cal = cal()
        self.dbfolder = dbfolder  
        self.contact()
        
        self.ui.date_debut.setDate(QDate.currentDate())
        self.ui.date_fin.setDate(QDate.currentDate().addDays(365))
        self.ui.resp.setEnabled(False)
        self.ui.lineEdit_3.setEnabled(False)
        self.ui.adresse.setEnabled(False)
        self.ui.name_entreprise.setEnabled(False)
        self.ui.mobile.setEnabled(False)
        self.ui.tel1.setEnabled(False)
        self.ui.detail.setEnabled(False)
        self.ui.pushButton_28.setEnabled(False)
        self.ui.pushButton_24.setEnabled(False)
        self.ui.pushButton_25.setEnabled(False)
        
        self.ui.checkBox_5.stateChanged.connect(self.active_saisi)
        self.ui.checkBox_5.stateChanged.connect(lambda state: self.active_saisi(state))
        Personal.aff_ut(self)
        
        Personal.af_img(self)
        
        self.ui.pushButton_28.clicked.connect(lambda: Personal.openImage(self))
        self.ui.pushButton_25.clicked.connect(lambda: Personal.modif_donnee(self))
        self.ui.pushButton_18.clicked.connect(lambda: Personal.aj_utlis(self)) 
        self.ui.pushButton_24.clicked.connect(lambda: Personal.enreg_exercice(self))   
        self.ui.pushButton.clicked.connect(self.add_mode)     
       
   
    def active_saisi(self,state):
        is_checked  = state == 2
        self.ui.resp.setEnabled(is_checked)
        self.ui.lineEdit_3.setEnabled(is_checked)
        self.ui.adresse.setEnabled(is_checked)
        self.ui.name_entreprise.setEnabled(is_checked)
        self.ui.mobile.setEnabled(is_checked)
        self.ui.tel1.setEnabled(is_checked)
        self.ui.detail.setEnabled(is_checked)
        self.ui.pushButton_28.setEnabled(is_checked)
        self.ui.pushButton_24.setEnabled(is_checked)
        self.ui.pushButton_25.setEnabled(is_checked)
        self.ui.date_fin.setEnabled(is_checked)
        self.ui.date_debut.setEnabled(is_checked)
        self.ui.lineEdit_4.setEnabled(is_checked)
        self.ui.doubleSpinBox.setEnabled(is_checked)
        self.ui.lineEdit_5.setEnabled(is_checked)
        self.ui.lineEdit_7.setEnabled(is_checked)
        self.ui.pushButton.setEnabled(is_checked)

    
    
    
    def enreg_exercice(self):
        dosier = "config"
        self.CONFIG_FILE = os.path.join(dosier,"config_magasin.json")
        ifu = self.ui.lineEdit_5.text()
        autre = self.ui.lineEdit_7.text()
        nom = self.ui.name_entreprise.text().strip().upper()
        tele = self.ui.mobile.text().strip()
        tel1=self.ui.tel1.text().strip()
       
        detail=self.ui.detail.text().strip()
        nom_resp=self.ui.resp.text().strip()
        nom_resp = self.cal.nom_upper(nom_resp)
        adr=self.ui.lineEdit_3.text().strip()
        ville = self.ui.adresse.text().strip()
        
    
        if os.path.exists(dosier):  
            if nom == "":
                QMessageBox.warning(self, "ENREGISTREMENT","Nom de l'entreprise invalide ou vide")
                self.ui.name_entreprise.setFocus()
            if tele =="": 
                QMessageBox.warning(self, "ENREGISTREMENT","Téléphone  invalide ou vide")
                self.ui.mobile.setFocus()                   
            if tel1 =="":
                QMessageBox.warning(self, "ENREGISTREMENT", "Ajouter un numéro whatsApp")
                self.ui.tel1.setFocus()
            if detail =="":
                QMessageBox.warning(self, "ENREGISTREMENT", "Ajouter des information sur le magasin")
                self.ui.detail.setFocus()
            if nom_resp =="":
                QMessageBox.warning(self, "ENREGISTREMENT", "Nom du responsable invalide ou vide")
                self.ui.resp.setFocus()
            if ville =="":
                QMessageBox.warning(self, "ENREGISTREMENT", "Ville invalide ou vide")
                self.ui.lineEdit_3.setFocus()
            if adr =="":                                    
                QMessageBox.warning(self, "ENREGISTREMENT", "Adresse invalide ou vide")
                self.ui.adresse.setFocus()    
            config = {
                "nom_entre":nom,
                "contact1":tele,
                "contact2":tel1,
                "responsable":nom_resp,
                "adresse":adr,
                "ville":ville,
                "detail":detail,
                "ifu":ifu,
                "autre":autre,
            }
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
                QMessageBox.information(self,"Configuration","Données enregistrer avec succè!")
        else:
            os.makedirs(dosier)
            config = {
                "nom_entre":nom,
                "contact1":tele,
                "contact2":tel1,
                "responsable":nom_resp,
                "adresse":adr,
                "ville":ville,
                "detail":detail,
                "ifu":ifu,
                "autre":autre,
            }
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
                QMessageBox.information(self,"Configuration","Période d'exercice enregistrer")
    
  
   
   
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
    def add_mode(self):
        conn = cal.connect_to_db(self.dbfolder)
        if conn is None:
            return
        cur = conn.cursor()
        dosier = "config"
        self.CONFIG_FILE = os.path.join(dosier,"config_mode.json")
        date_fin = self.ui.date_fin.text()
        date_debute = self.ui.date_debut.text()

        date_debute = datetime.strptime(date_debute, "%Y-%m-%d").date()
        date_fin = datetime.strptime(date_fin, "%Y-%m-%d").date()
        devise = self.ui.lineEdit_4.text()
        tva = self.ui.doubleSpinBox.value()
        if self.ui.radioButton.isChecked():
            self.mode_depot = "Simple dépôt"
        else:
            self.mode_depot = "Multi-dépôts"
        if date_debute > date_fin:
            QMessageBox.information(self,"Information","La date du début ne peut pas être postérieure à la date de fin")
        else:
            enreg = f""" insert INTO config (mode_depot) VALUES (?);                                        
                                    """
            liset_empl=(self.mode_depot)
            cur.execute(enreg, liset_empl)
            if os.path.exists(dosier):  
                config = {
                    "debut_exercice": f"{date_debute}",
                    "fin_exercice": f"{date_fin}",
                    "devise":f"{devise}",
                    "tva":f"{tva}",
                    
                    }
                try:
                    with open(self.CONFIG_FILE, "r") as f:
                        data = json.load(f)
                        if not isinstance(data,dict):
                            data = {}
                except (FileNotFoundError,json.JSONDecodeError):
                    data={}
                for l, j in config.items():
                    if l not in data:
                        data[l] = j
                    else:
                        if not isinstance(data[l],list):
                            data[l] = [data[l]]
                        data[l].append(j)
                with open(self.CONFIG_FILE, "w") as f:
                    json.dump(config, f,ensure_ascii=False, indent=4)
                    QMessageBox.information(self,"Configuration","Données enregistrer avec succè!")
                    conn.commit()
            
   
    def aj_utlis(self):
        conn = cal.connect_to_db(self.dbfolder)
        if conn is None:
            return QMessageBox.warning(self, "Erreur", "Impossible de se connecter à la base de données.")
        cur = conn.cursor()
        nom = self.ui.lineEdit.text().strip()
        mot = self.ui.lineEdit_6.text()
        mot_ = hash_password(mot)
        id_ui = self.ui.lineEdit_2.text().strip()
    
        try:

            if Personal.verifie_mot(self,mot):
                if Personal.verifie_mot(self,id_ui):
                    if nom != "":
                        enreg = f""" insert INTO login (nom, paswrd, id_int) VALUES (?,?,?);                                        
                                    """
                        liset_empl=(nom,mot_,id_ui)
                        cur.execute(enreg, liset_empl)
                        msg = QMessageBox(self)
                        msg.setWindowTitle("ENREGISTREMENT")
                        msg.setText("Etes vous sur de vouloir enregistrer ces données?")
                        btn_yes = msg.addButton("Oui",QMessageBox.ButtonRole.YesRole)
                        btn_n = msg.addButton("Non",QMessageBox.ButtonRole.NoRole)
                        msg.exec()
                        if msg.clickedButton() == btn_yes:
                            conn.commit()

                        else:
                            conn.rollback()
                        
                        conn.close()
                        Personal.aff_ut(self)
                        
                        self.ui.lineEdit.clear()
                        self.ui.lineEdit_2.clear()
                        
                        self.ui.lineEdit_6.clear()
                                    
                    else:
                        QMessageBox.warning(self, "ENREGISTREMENT", "Nom invalide ou vide")
                        self.ui.lineEdit.setFocus()
                        self.ui.lineEdit.selectAll()  
                else:
                    QMessageBox.warning(
                        self, "ENREGISTREMENT", "L'identifiant incorrecte. Votre identifiant doit contenir au mois des lettres,symboles et chiffres")
                    self.ui.lineEdit_2.setFocus()  
                        
            else:
                QMessageBox.warning(self, "ENREGISTREMENT","Mot de passe  invalide. Votre mot de passe doit contenir au mois des lettres , symboles et chiffres")
                self.ui.lineEdit_6.setFocus()
                self.ui.lineEdit_6.selectAll()                   
                            
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)}")
            QMessageBox.warning(self, "ENREGISTREMENT", f"Enregistrement echoué:{e}")
        conn.close()
       
  

    def aff_ut(self):
        try:
            
            conn = cal.connect_to_db(self.dbfolder)
            if conn is None:
                return QMessageBox.warning(self, "Erreur", "Impossible de se connecter à la base de données.")
            cur = conn.cursor()
            sql = '''SELECT * from login'''
            cur.execute(sql)
            result = cur.fetchall()
            self.ui.tableWidget_5.setRowCount(0)
            for nbr_row, nbr_data in enumerate(result):
                self.ui.tableWidget_5.insertRow(nbr_row)
                for col, data in enumerate(nbr_data):
                    self.ui.tableWidget_5.setItem(nbr_row, col, QTableWidgetItem(str(data)))
            
            cur.close()
            conn.close()
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Erreur: {e}")

    def contact(self):
        self.ui.mobile.setValidator(self.cal.contact_validator(self.ui.mobile))
        self.ui.tel1.setValidator(self.cal.contact_validator(self.ui.tel1))
    
                       
       

    def modif_donnee(self):
        try:
            conn = cal.connect_to_db(self.dbfolder)
            if conn is None:
                return QMessageBox.warning(self, "Erreur", "Impossible de se connecter à la base de données.")
            cur = conn.cursor()

            nomE = self.ui.name_entreprise.text().strip()
            te = self.ui.mobile.text().strip()
            tel1=self.ui.tel1.text().strip()
            detail = self.ui.detail.text().strip()
            nom_resp=self.ui.resp.text().strip()
            ville=self.ui.adresse.text().strip()
            adr = self.ui.lineEdit_3.text().strip()
            regex = QRegularExpression(r'^\+?\d{0,15}$')
            validator = QRegularExpressionValidator(regex,self.ui.mobile)
            validator_a = QRegularExpressionValidator(regex,self.ui.tel1)
            self.ui.mobile.setValidator(validator)
            self.ui.tel1.setValidator(validator_a)
            if nomE != "":
                if te !="": 
                    if tel1 !="":
                        if detail !="":
                            if nom_resp !="":
                                if ville !="":
                                    if adr !="":
                                        try:
                                            ligne = (te,tel1,detail,nom_resp,adr,nomE,ville)
                                            cmd = '''UPDATE  infoentre set tele=?,tele1=?,detail=?,nom1=?,adr=? ,nom=?,ville =?'''
                                            cur.execute(cmd, ligne)
                                            msg = QMessageBox(self)
                                            msg.setWindowTitle("MODIFICATION")
                                            msg.setText("Êtes vous sur de vouloir modifier ces informations ")
                                            btn_yes = msg.addButton("Oui",QMessageBox.ButtonRole.YesRole)
                                            btn_no = msg.addButton("Non",QMessageBox.ButtonRole.NoRole)
                                            msg.exec()
                                            if msg.clickedButton() == btn_yes:
                                                conn.commit()
                                                
                                                QMessageBox.information(self,"Modification","Les informations ont été modifié avec succès!!")
                                            else:
                                                conn.rollback()
                                            
                                        except Exception as e:
                                            QMessageBox.warning(self,"Erreur",f"{e}")
                                            
                                        self.ui.name_entreprise.clear()
                                        self.ui.mobile.clear()           
                                        self.ui.detail.clear()
                                        self.ui.lineEdit_3.clear()
                                        self.ui.tel1.clear()
                                        self.ui.resp.clear()
                                        self.ui.adresse.clear()
                                        
                                        conn.close()
                                    else:
                                        QMessageBox.warning(self, "Modification", "Adresse  invalide ou vide")
                                        self.ui.detail.setFocus()
                                else:
                                    QMessageBox.warning(self, "Modification", "Ville  invalide ou vide")
                                    self.ui.adresse.setFocus()
                            else:
                                QMessageBox.warning(self, "Modification", "Nom responsable  invalide ou vide")
                                self.ui.resp.setFocus()
                        else:
                            QMessageBox.warning(self, "Modification", "Details  invalide ou vide")
                            self.ui.detail.setFocus()
                    else:
                        QMessageBox.warning(self, "Modification", "Contact 2  invalide ou vide")
                        self.ui.tel1.setFocus()
                else:
                    QMessageBox.warning(self, "Modification", "Contact 1  invalide ou vide")
                    self.ui.mobile.setFocus()
            else:
                QMessageBox.warning(self, "Modification", "Nom entreprise invalide ou vide")
                self.ui.name_entreprise.setFocus()
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)}")
    def af_img(self):
        chemin = "logo"
        try:
            self.defaulImgSrc = os.listdir(chemin)[0]
            self.file_chemin = os.path.join(chemin, self.defaulImgSrc)
            self.image = QPixmap(self.file_chemin)
            self.ui.image.setPixmap(self.image.scaled(self.ui.image.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        except:
            pass
    
    def openImage(self):
        size = (200, 200)
        dosier="logo"
        self.filename, ok = QFileDialog.getOpenFileName(
            self, "Charger Image", '', "Image Files (*.png)")
        self.image = QPixmap(self.filename)
        try:
            img = Image.open(self.filename)
        except:
            pass
        if ok:
            try:
                
                productImg = os.path.basename(self.filename)
                img = Image.open(self.filename)
                img = img.resize(size)
                if os.path.exists(dosier):                    
                    img.save("logo/{0}".format(productImg))
                else:
                    os.makedirs(dosier)
                    img.save("logo/{0}".format(productImg))
                self.ui.image.setPixmap(QPixmap('logo/{}'.format(productImg)))
                self.ui.image.setPixmap(
                    self.image.scaled(self.ui.image.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            except:
                pass
        Personal.af_img(self)
 
 