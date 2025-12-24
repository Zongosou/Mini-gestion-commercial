# auteur: zongo soumaïla
# Tel: +226 56832442 / 70925613
import json
import os
from PySide6.QtWidgets import QDoubleSpinBox,QComboBox,QTableWidget
import re
import sqlite3 as sq
from PySide6.QtCore import Qt,QSettings,QRegularExpression,QAbstractTableModel
from PySide6.QtGui import QRegularExpressionValidator,QColor, QBrush
import datetime


class PandasModel(QAbstractTableModel):
    """
    Un modèle de table qui affiche les données d'un DataFrame Pandas.
    """
    def __init__(self, data):
        super().__init__()
        self._df = data
        self.cal = cal()
        self._column_map = {
            'factu': 'Facture',
            'datee': 'Date',
            'montant': 'Montant',
            'monn': 'Restant',
            'statut': 'Statut',
            'id_fr': 'ID Fournisseur',
            'mnt_ttc': 'Montant TTC',
            'reste': 'Restant',
            'type_piece': 'Type de Pièce',
            'compta': 'Comptabilité',
            'payer': 'Payé',
            'payé': 'Payé',
            'client': 'ID Client',
            'type_fact': 'Type de Facture'
        }

    def rowCount(self, parent=None):
        """Retourne le nombre de lignes du DataFrame."""
        return self._df.shape[0]

    def columnCount(self, parent=None):
        """Retourne le nombre de colonnes du DataFrame."""
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Retourne les données et gère le style des cellules."""
        if not index.isValid():
            return None
        
        df_row = self._df.iloc[index.row()]
        col_name = self._df.columns[index.column()]
        value = df_row[col_name]

        if role == Qt.ItemDataRole.DisplayRole:
            devise = self.cal.charger_tva_devise()
            
            if devise is None:
                return None
            devise = devise.get("devise", "XOF") # Utilisez une valeur par défaut en cas de non-existence
            
            if col_name == 'datee':
                # Convertit la chaîne en objet datetime, puis formate-le
                try:
                    # Tente de convertir la chaîne de caractères
                    return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S").date().strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    # En cas d'échec de la conversion, retourne la valeur d'origine ou une chaîne vide
                    return str(value)
            elif col_name in ['montant', 'prix', 'reste', 'mnt_ttc', 'monn', 'payé', 'payer']:
                return f"{value:.2f} {devise}"
            return str(value)
        
        if role == Qt.ItemDataRole.BackgroundRole:
            # Vérifiez si la colonne 'statut' existe avant d'essayer d'y accéder
            if 'statut' in df_row:
                statut = str(df_row['statut'])
                if statut == "Impayé" or statut == "Payer":
                    return QBrush(QColor(255, 200, 200))
        
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Définit les en-têtes de colonnes en utilisant la carte de correspondance. 
           Si les en-têtes par défaut ne correspondent pas, utilise les noms de colonnes par défaut."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Utilise .get() avec une valeur par défaut pour éviter les erreurs
                # si le nom de la colonne n'est pas dans la carte.
                return str(self._column_map.get(self._df.columns[section], self._df.columns[section])).upper()
            else:
                return str(self._df.index[section]+1) 
        return None

CONFIG_FOLDER = 'config'

class cal:
    def __init__(self) -> None:
        super().__init__()
    
    @staticmethod  
    def connectioan(db_file):
        conn = None
        try:
            conn = sq.connect(db_file)
        except sq.Error:
            pass
        return conn
    # calcul de la remise
    def remis(self,ht:float,remis:float):
        try:
            remis = float(remis)
            ht = float(ht)
            mnt_remis = float(ht*(remis / 100))
            return mnt_remis
        except:
            pass
    #  calcul de la valeur ajoutee
    def tva(self,ht:float,tva:float):
        try:
            tva = float(tva)
            ht = float(ht)
            mnt_ttc =round(float(ht * (1 + (tva / 100))),2)
            return mnt_ttc
        except:
            pass
        
    # calcul de la valeur finale
    def net(self, taux_remis:float,taux_tva:float,mnt_ht:float):
        try:          

            mnt_ttc = (self.tva(mnt_ht,taux_tva))
            if mnt_ttc is None:
                return
            mnt_remis = (self.remis(mnt_ht,taux_remis))
            if mnt_remis is None:
                return
            net = (mnt_ttc) - mnt_remis
            return net
        except ValueError:
            pass
    def contact_validator(self,text):
        regex = QRegularExpression(r'^\+?\d{0,15}$')
        validator = QRegularExpressionValidator(regex,text) 
        return validator
    def contact_valid(self,contact:str):
        contact=str(contact)
        text_re=re.compile(r'^\+\d{11}$')
        if text_re.match(contact):
            return True
        else:
            return False 
    def recup_donnee(self,tab:QTableWidget):
        donne=[]
        for row in range(tab.rowCount()):
            row_data=[]
            for col in range(tab.columnCount()):
                item=tab.item(row,col) 
                if item:
                    row_data.append(item.text())
                
                elif tab.cellWidget(row,col):
                    widget=tab.cellWidget(row,col)
                    if isinstance(widget,QDoubleSpinBox):
                        row_data.append(str(widget.value()))
                    elif isinstance(widget,QComboBox):
                        dat = widget.currentData()
                        row_data.append(str(dat) if dat is not None else widget.currentText())
            donne.append(tuple(row_data))
        return donne
    
    def verifi_exit(self,tab:QTableWidget,item_exi):
        for ligne in range(tab.rowCount()):
            for col in range(tab.columnCount()):
                item=tab.item(ligne,col)
                if item and item.text()==item_exi:
                    return True
        return False
    
    def print_info(self,dbfolder): 
        try:
            conn = cal.connect_to_db(dbfolder)
            if conn is None:
                return
            cur = conn.cursor()
            sqls = '''SELECT * from infoentre'''
            cur.execute(sqls)
            resu = cur.fetchone()
            if resu:
                nom = resu[0]            
                tel = resu[1]
                tel1=resu[2]
                detail=resu[3]
                nom_resp=resu[4]
                adr=resu[5]
                ville = resu[6]
                info={"nom":nom,"T1":tel,"T2":tel1,"info":detail,"resp":nom_resp,"adresse":adr,"ville":ville,"ifu":resu[7],"autre":resu[8]}
                return info
            else:
                pass
        except Exception as e:
            pass
    
    def random_client(self):
        try:
            setting_file = os.path.join(CONFIG_FOLDER, "client.ini")
            settings = QSettings(setting_file, QSettings.Format.IniFormat)
            self.nombre=settings.value("clt",0,type=int)
    
            self.nombre = int(self.nombre) + 1
            settings.setValue("clt",self.nombre)
            return f"CL{self.nombre:03}"
        except Exception as e:
            pass
   
     
    def numero_comd(self):
        
        setting_file = os.path.join(CONFIG_FOLDER, "settign2.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.anne=datetime.datetime.now().year
        self.mois = datetime.datetime.now().month
        self.nombre=settings.value("numb1",0,type=int)
        if not settings.contains("annee"):
            settings.setValue("annee",self.anne)
        if not settings.contains("mois"):
            settings.setValue("mois",self.mois)
            
        self.an=settings.value("annee",0,type=int)
        self.moi=settings.value("mois",0,type=int)
    
        if self.an !=self.anne or self.moi !=self.mois:
            self.nombre = 1
            settings.setValue("annee",self.anne)
            settings.setValue("mois",self.mois)
        else:
            self.nombre += 1
        settings.setValue("numb1",self.nombre)
        
        return f"C-{self.anne}-{self.mois:02}-{self.nombre:03}"
    def numero_comd_ent(self):
        
        setting_file = os.path.join(CONFIG_FOLDER, "settign2.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.anne=datetime.datetime.now().year
        self.mois = datetime.datetime.now().month
        self.nombre=settings.value("numb1",0,type=int)
        if not settings.contains("annee"):
            settings.setValue("annee",self.anne)
        if not settings.contains("mois"):
            settings.setValue("mois",self.mois)
            
        self.an=settings.value("annee",0,type=int)
        self.moi=settings.value("mois",0,type=int)
    
        if self.an !=self.anne or self.moi !=self.mois:
            self.nombre = 1
            settings.setValue("annee",self.anne)
            settings.setValue("mois",self.mois)
        else:
            self.nombre += 1
        settings.setValue("numb1",self.nombre)
        
        return f"CR-{self.anne}-{self.mois:02}-{self.nombre:03}"
    
    def numero_facture_achat(self):
        try:
            
            setting_file = os.path.join(CONFIG_FOLDER, "achat.ini")
            settings = QSettings(setting_file, QSettings.Format.IniFormat)
            self.anne=datetime.datetime.now().year
            self.mois = datetime.datetime.now().month
            self.nombre=settings.value("numb_ach",0,type=int)
            if not settings.contains("annee"):
                settings.setValue("annee",self.anne)
            if not settings.contains("mois"):
                settings.setValue("mois",self.mois)    
            self.an=settings.value("annee",0,type=int)
            self.moi=settings.value("mois",0,type=int)
            if self.an !=self.anne:   
                self.nombre = 1
                settings.setValue("annee",self.anne)
                settings.setValue("mois",self.mois)    
            else:
                self.nombre += 1   
            settings.setValue("numb_ach",self.nombre)
            return f"FA-{self.anne}-{self.mois:02}-{self.nombre:03}"
        except:
            pass
    def numero_facture_preview(self):
        settings = QSettings(os.path.join(CONFIG_FOLDER, "vente.ini"),
                            QSettings.Format.IniFormat)

        annee = datetime.datetime.now().year
        mois = datetime.datetime.now().month
        nombre = settings.value("fact", 0, type=int) + 1

        return f"F-{annee}-{mois:02}-{nombre:03}"

    def numero_inv(self):
        try:
            
            setting_file = os.path.join(CONFIG_FOLDER, "inv.ini")
            settings = QSettings(setting_file, QSettings.Format.IniFormat)
            self.anne=datetime.datetime.now().year
            self.mois = datetime.datetime.now().month
            self.nombre=settings.value("invent",0,type=int)
            
            if not settings.contains("annee"):
                settings.setValue("annee",self.anne)
            if not settings.contains("mois"):
                settings.setValue("mois",self.mois)
                
            self.an=settings.value("annee",0,type=int)
            self.moi=settings.value("mois",0,type=int)
            
            
            if self.an !=self.anne:
                
                self.nombre = 1
                settings.setValue("annee",self.anne)
                settings.setValue("mois",self.mois)
            else:
                self.nombre += 1
                
            settings.setValue("invent",self.nombre)
            return f"INV-{self.anne}-{self.mois:02}-{self.nombre:03}"
        except Exception as e:
            print(e)
     
    def numero_liv(self):
        
        setting_file = os.path.join(CONFIG_FOLDER, "bliv.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.anne=datetime.datetime.now().year
        self.mois = datetime.datetime.now().month
        self.nombre=settings.value("numb_bl",0,type=int)
        if not settings.contains("annee"):
            settings.setValue("annee",self.anne)
        if not settings.contains("mois"):
            settings.setValue("mois",self.mois)
            
        self.an=settings.value("annee",0,type=int)
        self.moi=settings.value("mois",0,type=int)
    
        if self.an !=self.anne or self.moi !=self.mois:
            self.nombre = 1
            settings.setValue("annee",self.anne)
            settings.setValue("mois",self.mois)
        else:
            self.nombre += 1
        settings.setValue("numb_bl",self.nombre)
        
        return f"BL-{self.anne}-{self.mois:02}-{self.nombre:03}"
    
    def numero_recep(self):
        
        setting_file = os.path.join(CONFIG_FOLDER, "brcp.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.anne=datetime.datetime.now().year
        self.mois = datetime.datetime.now().month
        self.nombre=settings.value("numb_rept",0,type=int)
        if not settings.contains("annee"):
            settings.setValue("annee",self.anne)
        if not settings.contains("mois"):
            settings.setValue("mois",self.mois)
            
        self.an=settings.value("annee",0,type=int)
        self.moi=settings.value("mois",0,type=int)
    
        if self.an !=self.anne or self.moi !=self.mois:
            self.nombre = 1
            settings.setValue("annee",self.anne)
            settings.setValue("mois",self.mois)
        else:
            self.nombre += 1
        settings.setValue("numb_rept",self.nombre)
        
        return f"BR-{self.anne}-{self.mois:02}-{self.nombre:03}"
    


    def numero_devi_pro(self):
        
        
        setting_file = os.path.join(CONFIG_FOLDER, "devis.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.anne=datetime.datetime.now().year
        self.mois = datetime.datetime.now().month
        self.nombre=settings.value("numb_dev",0,type=int) 
        if not settings.contains("annee"):
            settings.setValue("annee",self.anne)
        if not settings.contains("mois"):
            settings.setValue("mois",self.mois)  
        self.an=settings.value("annee",0,type=int)
        self.moi=settings.value("mois",0,type=int)
        if self.an !=self.anne:   
            self.nombre = 1
            settings.setValue("annee",self.anne)
            settings.setValue("mois",self.mois)    
        else:
            self.nombre += 1   
        settings.setValue("numb_dev",self.nombre)
        return f"DVI-{self.nombre:03}-{self.anne}"
    
     
    def random_recette(self):
       
        setting_file = os.path.join(CONFIG_FOLDER, "caisse.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.anne=datetime.datetime.now().year
        self.mois = datetime.datetime.now().month
        self.nombre=settings.value("numb",0,type=int)
        if not settings.contains("annee"):
            settings.setValue("annee",self.anne)
        if not settings.contains("mois"):
            settings.setValue("mois",self.mois)
            
        self.an=settings.value("annee",0,type=int)
        self.moi=settings.value("mois",0,type=int)
        
        if self.an !=self.anne:
            self.nombre = 1
            settings.setValue("annee",self.anne)
            settings.setValue("mois",self.mois)
        else:
            self.nombre += 1
        settings.setValue("numb",self.nombre)
        return f"REF{self.anne}{self.mois:02}-{self.nombre:03}"
    
    def random_prop(self):
     
        setting_file = os.path.join(CONFIG_FOLDER, "produit.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.nombre=settings.value("numb_rep",0,type=int)
        self.nombre += 1   
        settings.setValue("numb_rep",self.nombre)
        return f"PRD{self.nombre:03}"

    def load_json(self):
        setting_file = os.path.join(CONFIG_FOLDER, "moyen.json")
        with open(setting_file,'r',encoding='utf-8') as f:
            return json.load(f)


    def count_nbr(self):
     
        setting_file = os.path.join(CONFIG_FOLDER, "count.ini")
        settings = QSettings(setting_file, QSettings.Format.IniFormat)
        self.anne=datetime.datetime.now().year
        
        self.nombre=settings.value("numb",0,type=int)
        if not settings.contains("annee"):
            settings.setValue("annee",self.anne)            
        self.an=settings.value("annee",0,type=int)
        
        if self.an !=self.anne:
            self.nombre = 1
            settings.setValue("annee",self.anne)
            
        else:
            self.nombre += 1
        settings.setValue("numb",self.nombre)
        return f"{self.anne}-{self.nombre:03}"

    @staticmethod
    def connect_to_db(db_file):
        """
        Établit une connexion à la base de données SQLite.
        """
        try:
            return sq.connect(db_file)
        except sq.Error as e:
            return None
    
    def extrait_data(self,table:QTableWidget):
        rows = table.rowCount()
        cols = table.columnCount()
        data = []
        for row in range(rows):
            rows_data ={}
            for col in range(cols):
                header = table.horizontalHeaderItem(col)
                if header is None:
                    return
                header = header.text()
                celle_values = table.item(row,col)
                if celle_values is None:
                    return
                celle_values = celle_values.text()
                rows_data[header] = celle_values
            data.append(rows_data)
        
        return data
    
    def nom_upper(self,text: str):
        word = text.split()
        if len(word) >= 2:
            text_format = word[0].upper() + " " + word[1].capitalize()
        elif len(word) == 1:
            text_format = word[0].upper()
        else:
            text_format = ""
        return text_format

    def code_paiement(self,methode:str) ->str:
        """Return the payment code based on the payment method.

            Args:
                methode (str): The payment method.

            Returns:
                str: The payment code, which is the first two uppercase characters of the stripped payment method.
                     Returns an empty string if the payment method is None or empty.
            """
        return methode.strip()[:2].upper() if methode else ""
    
    # def charger_fatu_maga(self):
    #     """Charge la configuration depuis un fichier JSON."""
    #     try:
    #         conn = cal.connect_to_db(dbfolder)
    #         if conn is None:
    #             return
    #         cur = conn.cursor()
    #         sqls = '''SELECT * from infoentre'''
    #         cur.execute(sqls)
    #         resu = cur.fetchone()
    #         if resu:
    #             nom = resu[0]            
    #             tel = resu[1]
    #             tel1=resu[2]
    #             detail=resu[3]
    #             nom_resp=resu[4]
    #             adr=resu[5]
    #             ville = resu[6]
    #             info={"nom":nom,"T1":tel,"T2":tel1,"info":detail,"resp":nom_resp,"adresse":adr,"ville":ville,"ifu":resu[7],"autre":resu[8]}
    #             return info
    #         else:
    #             pass
    #     except FileNotFoundError:
    #         pass
    
    def charger_configuration_paie(self):
        """Charge la configuration depuis un fichier JSON."""
        setting_file = os.path.join(CONFIG_FOLDER, 'config_paie.json')
        
        try:
            with open(setting_file, "r") as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            pass
    
    def charger_tva_devise(self,db_file):
        """Charge la configuration depuis un fichier JSON."""
        
        try:
            conn = cal.connect_to_db(db_file)
            if conn is None:
                return
            cur = conn.cursor()
            sqls = '''SELECT * from config'''
            cur.execute(sqls)
            resu = cur.fetchone()
            
            if resu:
                date_debu = resu[0]            
                date_fin = resu[1]
                devise=resu[2]
                tva=resu[3]
                
                
                info={"date_debu":date_debu,"date_fin":date_fin,"devise":devise,"tva":tva}
                return info
            
        except FileNotFoundError:
            pass
    def insert_tresorerie(self,cur, date_op, libelle, montant, type_op, compte,user):
        
        try:
            
            cur.execute("""
                INSERT INTO tresorerie (date_operation, libelle, montant, type, compte, reference, utilisateur)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date_op.strftime("%Y-%m-%d"), libelle, montant, type_op, compte,
                self.random_recette(), user))
           
            return True
        except Exception as e:
            return False
    
    def separateur_milieur(self,solde):
        return  f"{solde:,.2f}".replace(","," ").replace(".",",")


import sqlite3
import datetime
from fonction.methode import cal
class Numeroteur:
    def __init__(self, db):
        self.db = db
        self.cal =cal()
        # self._init_db()

    def _init_db(self):
        self.conn = self.cal.connect_to_db(self.db)
        if self.conn is None:
            return False
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS compteurs (
                piece TEXT PRIMARY KEY,
                annee INTEGER,
                mois INTEGER,
                valeur INTEGER
            )
        """)
        self.conn.commit()

    def preview(self, piece: str) -> str:
        """Aperçu SANS incrémenter (avant validation)"""
        now = datetime.datetime.now()
        return f"{piece}-{now.year}-{now.month:02}-XXX"
    def preview_prdo(self):
        self.conn = self.cal.connect_to_db(self.db)
        if self.conn is None:
            raise
        cur = self.conn.cursor()

        cur.execute(
            "SELECT MAX(id_prod) FROM products")
        last_id = cur.fetchone()[0]
        next_id = 1 if last_id is None else last_id + 1
        return f"PRO{next_id:03d}"

    def generer(self, piece: str, mensuel: bool = True) -> str:
        """
        Génère et incrémente le numéro APRES validation
        piece : FAC, AV, BL, REC, etc.
        mensuel : True => repart chaque mois, False => annuel
        """
        now = datetime.datetime.now()
        annee, mois = now.year, (now.month if mensuel else 0)
        self.conn = self.cal.connect_to_db(self.db)
        if self.conn is None:
            return False
        cur = self.conn.cursor()

        cur.execute(
            "SELECT annee, mois, valeur FROM compteurs WHERE piece = ?",
            (piece,)
        )
        row = cur.fetchone()

        if row is None or row[0] != annee or row[1] != mois:
            valeur = 1
            cur.execute(
                "INSERT OR REPLACE INTO compteurs (piece, annee, mois, valeur) VALUES (?, ?, ?, ?)",
                (piece, annee, mois, valeur)
            )
        else:
            valeur = row[2] + 1
            cur.execute(
                "UPDATE compteurs SET valeur = ?, annee = ?, mois = ? WHERE piece = ?",
                (valeur, annee, mois, piece)
            )

        self.conn.commit()
        if mensuel:
            return f"{piece}-{annee}-{mois:02}-{valeur:03}"
        return f"{piece}-{annee}-{valeur:04}"

    def annuler_piece(self, table: str, piece_id: int):
        """Annulation logique (ne touche PAS le compteur)"""
        self.conn = self.cal.connect_to_db(self.db)
        if self.conn is None:
            return False
        cur = self.conn.cursor()
        cur.execute(f"UPDATE {table} SET statut='ANNULEE' WHERE id=?", (piece_id,))
        self.conn.commit()

    def creer_avoir(self, facture_id: int, montant: float) -> str:
        """Crée un avoir lié à une facture"""
        numero = self.generer("AV")
        self.conn = self.cal.connect_to_db(self.db)
        
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO avoirs (numero, facture_id, date_avoir, montant) VALUES (?, ?, DATE('now'), ?)",
            (numero, facture_id, montant)
        )
        self.conn.commit()
        return numero
