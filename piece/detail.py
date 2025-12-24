# auteur: zongo soumaïla
# Tel: +226 56832442 / 70925613

from PySide6.QtWidgets import (QTableWidgetItem, QMessageBox,QDialog)
try:
    from num2words import num2words
except:
    pass
from interface.liste_ui import Ui_liste
import logging.config
from interface.edit_comd_ui import Ui_dialog_edi
from fonction.methode import cal
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
            'filename': 'app_vente.log',
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
        '__main__': { # Pour votre module principal
            'handlers': ['console', 'file'],
            'level': 'DEBUG', # Utile pour le développement
            'propagate': False
        },
        'etat_stock.caisse': { # Si vous voulez des logs spécifiques pour ce module
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)
  
class Details(QDialog):
    def __init__(self,dbfolder = None,dataframe= None,factu_nu=None) -> None:
        super().__init__()
        self.ui = Ui_liste()
        self.ui.setupUi(self)
        self.dbfolder = dbfolder
        self.tab = self.ui.tableWidget
        self.ui.pushButton_3.setEnabled(False)
        self.factu_nu = factu_nu
        self.cal = cal()
        self.ui.label_2.setText(str(self.factu_nu))
        self.load_data(dataframe)
        self.ui.pushButton_3.clicked.connect(lambda:self.mise_a_finale())
        self.ui.pushButton_2.clicked.connect(lambda:self.edit_donnee())
    
        
    def load_data(self,dataframe):

        for index, row in dataframe.iterrows():
            row_position = self.tab.rowCount()
            self.tab.insertRow(row_position)
            for col, header in enumerate(row.index):
                self.tab.setItem(row_position, col, QTableWidgetItem(str(row[header]))) 
    
    def edit_donnee(self):
        try:
            
            self.edit_cmd = QDialog()
            self.edim = Ui_dialog_edi()
            self.edim.setupUi(self.edit_cmd)
            self.edit_cmd.show()
            self.liste_ecart = []
            self.liste_code = []
            self.qte = 0.0
            self.edim.quantitLineEdit.valueChanged.connect(lambda: Details.mnt(self))
            self.edim.prixLineEdit.textChanged.connect(lambda: Details.mnt(self))
            self.edim.pushButton.clicked.connect(lambda: Details.update_table(self))
            self.tab3=self.tab
            if len(self.tab3.selectedItems())>0:
                select_ligne=self.tab3.selectedItems()[0].row()
                self.code = self.tab3.item(select_ligne,1)
                if self.code is None:
                    return
                self.code = self.code.text()
                libelle = self.tab3.item(select_ligne,2)
                if libelle is None:
                    return
                libelle = libelle.text()
                self.qt = self.tab3.item(select_ligne,3)
                if self.qt is None:
                    return
                self.qte =  float(self.qt.text())
                prix = self.tab3.item(select_ligne,4)
                if prix is None:
                    return
                prix = float(prix.text())
                #insertion dans les champs de saisies
                self.edim.codeLineEdit.setText(str(self.code))
                self.edim.produitLineEdit.setText(str(libelle))
                self.edim.quantitLineEdit.setValue(self.qte)
                self.edim.prixLineEdit.setText(str(prix))
            else:
                QMessageBox.information(self.edit_cmd,"Edition de la quantité",f"{Exception}")
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)} dans edit_donnee")
            QMessageBox.information(self.edit_cmd,"Edition de la quantité",f"Une erreur: {str(e)} dans edit_donnee")
    
    def mnt(self):        
        try:
            p=float(self.edim.prixLineEdit.text())
            q=self.edim.quantitLineEdit.value()
            pda=p*q
            self.edim.montantLineEdit.setText(str(pda))
            
        except:
            pass 
    def update_table(self):
        
        code = self.edim.codeLineEdit.text()
        libelle = self.edim.produitLineEdit.text()
        quantite = self.edim.quantitLineEdit.value()
        prix = float(self.edim.prixLineEdit.text())
        mnt = float(self.edim.montantLineEdit.text())
        msg = QMessageBox(self.edit_cmd)
        msg.setWindowTitle("Edition des données")
        msg.setText(f"Etes-vous sur de vouloir enregistrer les modifications?")
        btn_yes = msg.addButton("Oui",QMessageBox.ButtonRole.YesRole)
        btn_n = msg.addButton("Non",QMessageBox.ButtonRole.NoRole)
        
        msg.exec_()
        if msg.clickedButton() == btn_yes:
            if self.qte is None:
                return
            self.reste = self.qte-quantite
            ligne_a_mod = self.tab.currentRow()
            self.tab.setItem(ligne_a_mod, 1, QTableWidgetItem(str(code)))
            self.tab.setItem(ligne_a_mod, 2, QTableWidgetItem(str(libelle)))
            self.tab.setItem(ligne_a_mod, 3,QTableWidgetItem(str(quantite)))
            self.tab.setItem(ligne_a_mod, 4,QTableWidgetItem(str(prix)))
            self.tab.setItem(ligne_a_mod, 5,QTableWidgetItem(str(mnt)))
            self.tab.setItem(ligne_a_mod, 6,QTableWidgetItem(str(self.reste)))
            self.ui.pushButton_3.setEnabled(True)
            self.liste_code.append([self.code])
            self.liste_ecart.append([(self.reste)])
        
        else:
            pass
        self.edit_cmd.close()

    def get_data_by(self):
        liste_ecrt = {}
        liste_ecrt['L'] = []
        data_vente={}
        somme = 0.0
        
        data_vente['line_items'] = []
        for row in range(self.ui.tableWidget.rowCount()):
            if not self.ui.tableWidget.item(row, 0):
                continue
            factu = self.ui.tableWidget.item(row, 0)
            if factu is None:
                return
            factu = factu.text()
            code = self.ui.tableWidget.item(row, 1)
            if code is None:
                return
            code = code.text()
            qtite = self.ui.tableWidget.item(row,3)
            if qtite is None:
                return
            qtite =float(qtite.text())
            prix = self.ui.tableWidget.item(row, 4)
            if prix is None:
                return
            prix = float(prix.text())
            mnt = self.ui.tableWidget.item(row, 5)
            if mnt is None:
                return
            mnt = float(mnt.text())
            ecrt = self.ui.tableWidget.item(row, 6)
            somme +=mnt
            L = [code, ecrt.text() if ecrt else "0.0"]
            row_data = [factu, prix, qtite, mnt,factu,code]  
            if any(row_data):
                data_vente['line_items'].append(row_data)
                liste_ecrt["L"].append(L)
        return (data_vente if data_vente else {"Value":"vide"}),(somme if somme else 0.0),(liste_ecrt if liste_ecrt else {"value":["vide"]}) 
    
    def mise_a_finale(self):
        conn = cal.connect_to_db(self.dbfolder)
        if conn is None:
            return
        cur = conn.cursor()
        new_reste = 0.0
        factu = self.ui.label_2.text()
        selec = '''select payer,tva from infov where factu=?'''
        sele_execute = cur.execute(selec,[factu]).fetchone()

        Mont_payer = float(sele_execute[0])
        Tva = float(sele_execute[1])
        get_data = self.get_data_by()
        if get_data is None:
            return
        data_vente,mnt_th,liste_ecrt = get_data
        new_mnt_ttc = self.cal.tva(mnt_th,Tva)
        if new_mnt_ttc is None:
            return
        
        new_reste = new_mnt_ttc - Mont_payer
        
        if new_reste < 0:
            Mont_payer = new_mnt_ttc
            new_reste = 0.0
        else:
            new_reste = new_reste
        etat_qty = "UPDATE etat SET sortie =sortie - ? WHERE code = ? "
        update_qty = "UPDATE achat SET quantite = quantite + ? WHERE code = ? "
        
        for ind, data in liste_ecrt.items():
            for i, item in enumerate(data):
                cd = item[0]
                qty = item[1]
                if qty == False:
                    qty = 0.0
                
                cur.execute(update_qty, [qty, cd])
                cur.execute(etat_qty, [qty, cd])
        for cle, data in data_vente.items():
            for i, items in enumerate(data):
                cur.execute("update  vent set facture =?, prix =?,quantite =?,montant =? where facture= ? and code =?",items)
                  
        cur.execute("UPDATE  infov set factu=?, mnt_ttc =?,montant =?,monn=? where factu=? ",[factu,new_mnt_ttc,mnt_th,new_reste,factu])
        msg = QMessageBox(self.edit_cmd)
        msg.setWindowTitle("Edition des données")
        msg.setText(f"Etes-vous sur de vouloir enregistrer les modifications?")
        btn_yes = msg.addButton("Oui",QMessageBox.ButtonRole.YesRole)
        btn_n = msg.addButton("Non",QMessageBox.ButtonRole.NoRole)
        msg.exec_()
        if msg.clickedButton() == btn_yes:
            pass
            conn.commit()
        else:
            conn.rollback()   
        self.close()
        
 