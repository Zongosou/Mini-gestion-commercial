from PySide6.QtGui import  QIcon,QCursor
from PySide6.QtWidgets import (QDialog, QMessageBox, QPushButton, QVBoxLayout,
                             QTableWidget,QComboBox, QTableWidgetItem,QHBoxLayout,QCheckBox,QWidget,QInputDialog,QAbstractItemView)
import sqlite3 as sq
from PySide6.QtCore import Qt
from datetime import date
from fonction.methode import cal
# from interface.ajouclient_ui import Ui_clientoufour

STATUT_PIECE = {
    "Devis": ["En cours", "Validé", "Traité", "Annulée"],
    "Commande": ["En cours", "Validé", "Traité", "Annulée"],
    "Bon de livraison": ["En cours", "Validé", "Traité", "Annulée"],
    "Facture": ["En cours", "Validé", "Traité", "Annulée"]
}

class ReliquatManager(QDialog):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle("Traitement des reliquats")
        
        self.setWindowIcon(QIcon(':/icon/icone.png'))
        self.btn_traiter = QPushButton("Compléter les reliquats")
        self.btn_traiter.clicked.connect(self.completer_reliquats)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setTabKeyNavigation(True)
        self.table.setProperty("showDropIndicator", True)
        self.table.setDragEnabled(False)
        self.table.setDragDropOverwriteMode(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Code", "Produit", "Client", "Qté restante", "Qté initiale", "Facture"])

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.btn_traiter)
        self.setLayout(layout)
        self.charger_reliquats()

    def charger_reliquats(self):
        self.table.setRowCount(0)
        try:
            with sq.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT code, libelle, client, quantite, qtit_entente, facture
                    FROM liste 
                    WHERE quantite > 0
                """)
                lignes = cur.fetchall()

                for row_num, row_data in enumerate(lignes):
                    self.table.insertRow(row_num)
                    for col_num, value in enumerate(row_data):
                        self.table.setItem(row_num, col_num, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des reliquats : {str(e)}")

    def completer_reliquats(self):
        try:
            with sq.connect(self.db_path) as conn:
                cur = conn.cursor()

                cur.execute("""
                    SELECT client, code, facture, libelle, prix, quantite, qtit_entente, id_ui
                    FROM liste 
                    WHERE quantite > 0
                """)
                lignes = cur.fetchall()

                if not lignes:
                    QMessageBox.information(self, "Aucun reliquat", "Aucun article en attente de livraison/facturation.")
                    return

                for ligne in lignes:
                    client, code, facture, libelle, prix, qte_restante, qtit_entente, id_ui = ligne

                    cur.execute("SELECT quantite FROM achat WHERE code = ?", (code,))
                    stock_row = cur.fetchone()
                    stock_dispo = stock_row[0] if stock_row else 0

                    if stock_dispo == 0:
                        continue

                    qte_facturable = min(stock_dispo, qte_restante)
                    reste = qte_restante - qte_facturable
                    montant = round(prix * qte_facturable, 2)

                    if qte_facturable > 0:
                        cur.execute("UPDATE achat SET quantite = quantite - ? WHERE code = ?", (qte_facturable, code))

                        cur.execute("""
                            INSERT INTO vent (client, code, facture, libelle, prix, quantite, montant, datee, rest, id_ui)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            client, code, facture + "_suite", libelle, prix,
                            qte_facturable, montant, date.today().isoformat(), reste, id_ui
                        ))

                        cur.execute("""
                            UPDATE liste 
                            SET quantite = ?
                            WHERE code = ? AND facture = ?
                        """, (reste, code, facture))

                conn.commit()
                QMessageBox.information(self, "Succès", "Les reliquats disponibles ont été automatiquement facturés.")
                self.charger_reliquats()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")


class DialogueConversion(QDialog):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.cal = cal()
        self.setWindowTitle("Pièces à convertir")
        self.resize(500, 400)
        self.setWindowIcon(QIcon(':/icon/icone.png'))
        
        self.combo_type = QComboBox()
        LISTE_PIECES = ["Devis","Commande", "Bon de livraison", "Facture"]
        self.combo_type.addItems(LISTE_PIECES)
        self.combo_type.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.combo_type.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setTabKeyNavigation(True)
        self.table.setProperty("showDropIndicator", True)
        self.table.setDragEnabled(False)
        self.table.setDragDropOverwriteMode(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["", "N° pièce", "Client", "Date", "Montant"])

        btn_ok = QPushButton("Convertir")
        btn_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ok.clicked.connect(self.convertir_piece)
        btn_annuler.clicked.connect(self.reject)
        self.combo_type.currentTextChanged.connect(self.charger_pieces)

        layout_main = QVBoxLayout()
        layout_main.addWidget(self.combo_type)
        layout_main.addWidget(self.table)

        btns = QHBoxLayout()
        btns.addWidget(btn_ok)
        btns.addWidget(btn_annuler)

        layout_main.addLayout(btns)
        self.setLayout(layout_main)

        self.charger_pieces()

    def charger_pieces(self):
        type_piece = self.combo_type.currentText()
        self.table.setRowCount(0)

        try:
            with sq.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT factu, client, datee, montant
                    FROM infov
                    WHERE type_fact = ? AND statut = 'Validé'
                """, (type_piece,))
                resultats = cur.fetchall()

                for row_num, ligne in enumerate(resultats):
                    self.table.insertRow(row_num)
                    checkbox = QCheckBox()
                    checkbox_widget = QWidget()
                    layout = QHBoxLayout(checkbox_widget)
                    layout.addWidget(checkbox)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.setContentsMargins(0, 0, 0, 0)
                    self.table.setCellWidget(row_num, 0, checkbox_widget)

                    for col_num, val in enumerate(ligne):
                        self.table.setItem(row_num, col_num + 1, QTableWidgetItem(str(val)))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement des pièces : {e}")

    def convertir_piece(self):
        selected = None
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if widget and widget.findChild(QCheckBox).isChecked():
                selected = row
                break

        if selected is None:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez cocher une pièce à convertir.")
            return

        self.table.selectRow(selected)
        add_ =self.add_ajt()
        if add_ is None:
            return

        res, resultat, client, cb_ = add_
        if not res:
            return

        type_origine = self.combo_type.currentText()
        factu_origine = res[0]

        type_cible, ok = QInputDialog.getItem(
            self, "Conversion", "Convertir en :", cb_, editable=False
        )
        if not ok or not type_cible:
            return

        if type_cible == "Commande":
            nouveau_numero = self.cal.numero_comd()
        elif type_cible == "Bon de livraison":
            nouveau_numero = self.cal.numero_liv()
        elif type_cible == "Facture":
            nouveau_numero = self.cal.numero_facture()
        else:
            QMessageBox.warning(self, "Erreur", "Type de conversion inconnu.")
            return

        try:
            with sq.connect(self.db_path) as conn:
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO infov (factu, client, montant, mnt_ttc, payer, monn, datee, statut, tva, type_fact, compta,origine)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                """, (
                    nouveau_numero, res[1], res[2], res[3], 0.0, res[5], res[8],
                    "En cours", res[6], type_cible,res[10],res[0]
                ))
                if type_cible == "Facture":
                    for article in resultat:
                        code, libelle, quantite, prix, montant = article
                        cur.execute("""
                            INSERT INTO vent (client,code,facture, libelle, prix,quantite,montant,datee,id_clt)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            client, code, nouveau_numero, libelle, prix, quantite, montant, res[8], res[1]
                        ))
                        cur.execute("UPDATE infov SET statut = 'Impayé' WHERE factu = ?", (factu_origine,))
                else:
                    for article in resultat:
                        code, libelle, quantite, prix, montant = article
                        cur.execute("""
                            INSERT INTO liste (client, code, facture, libelle, prix, quantite, montant, datee, id_clt)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            client, code, nouveau_numero, libelle, prix, quantite, montant, res[6], res[1]
                        ))
                    cur.execute("UPDATE infov SET statut = 'Traité' WHERE factu = ?", (factu_origine,))
                conn.commit()

            QMessageBox.information(self, "Succès", f"{type_origine} {factu_origine} converti en {type_cible} ({nouveau_numero})")
            self.charger_pieces()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du transfert : {e}")

    def add_ajt(self):
        conn = cal.connect_to_db(self.db_path)
        if conn is None:
            QMessageBox.warning(self, "Erreur", "Impossible de se connecter à la base de données.")
            return None, [], "", []
        cur = conn.cursor()
        try:
            index = None
            for row in range(self.table.rowCount()):
                widget = self.table.cellWidget(row, 0)
                if widget and widget.findChild(QCheckBox).isChecked():
                    index = row
                    break
            if index is None:
                QMessageBox.warning(self, "Transfert", "Veuillez cocher une ligne à convertir!")
                return None, [], "",[]

            va_item = self.table.item(index, 1)
            va = va_item.text() if va_item else ""
            sql = '''SELECT * FROM infov WHERE factu=?'''
            cur = cur.execute(sql, [va])
            res = cur.fetchone()
            if not res:
                QMessageBox.warning(self, "Transfert", "Pièce introuvable.")
                return [], [], "",[]

            if res[7] != "Validé":
                QMessageBox.warning(self, "Conversion refusée", f"La pièce sélectionnée n’est pas validée. Statut actuel : {res[7]}")
                return [], [], "",[]
            cb_ = []
            resultat = []
            type_fact = self.combo_type.currentText()
            self.type = type_fact
            if self.type == "Devis":
                cb_ = ["Commande", "Bon de livraison", "Facture"]
            elif self.type == "Commande":
                cb_ = ["Bon de livraison", "Facture"]
            elif self.type == "Bon de livraison":
                cb_ = ["Facture"]

            deta = '''SELECT code, libelle, quantite, prix, montant FROM liste WHERE facture=?'''
            resultat = cur.execute(deta, [va]).fetchall()
            if not resultat:
                QMessageBox.information(self, "Erreur", "Liste des articles indisponible")
                return [], [], "", []
            try:
                ui = '''SELECT client FROM liste WHERE facture=?'''
                client = str(cur.execute(ui, [va]).fetchone()[0])
            except:
                QMessageBox.information(self, "Erreur", "Information du client indisponible")
                client = ""

            return res, resultat, client, cb_

        except Exception as e:
            QMessageBox.information(self, "Erreur", f"Erreur : {e}")

class ValidationPieces(QDialog):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle("Valider des pièces")
        self.resize(600, 450)
        self.setWindowIcon(QIcon(':/icon/icone.png'))
        
        self.combo_type = QComboBox()
        self.combo_type.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.combo_type.addItems(["Selectionner le Type de Pièce","Devis", "Commande", "Bon de livraison","Facture"])
        self.combo_type.currentTextChanged.connect(self.charger_pieces)
        self.combo_statut = QComboBox()
        self.combo_statut.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setTabKeyNavigation(True)
        self.table.setProperty("showDropIndicator", True)
        self.table.setDragEnabled(False)
        self.table.setDragDropOverwriteMode(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Valider", "N° Pièce", "Client", "Date", "Montant"])

        self.btn_valider = QPushButton("Valider la sélection")
        self.btn_valider.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_valider.clicked.connect(self.valider_selection)
        box_h = QHBoxLayout()
        box_h.addWidget(self.combo_type)
        box_h.addWidget(self.combo_statut)
        layout = QVBoxLayout()
        layout.addLayout(box_h)
        layout.addWidget(self.table)
        layout.addWidget(self.btn_valider)
        
        self.setLayout(layout)
        self.charger_pieces()

    def get_statut(self,piece:str):
        return STATUT_PIECE.get(piece,[])
    
    def mette_a_jour(self,piece):
        self.combo_statut.clear()
        self.combo_statut.addItems(self.get_statut(piece))
    def charger_pieces(self):
        type_piece = self.combo_type.currentText()
        self.table.setRowCount(0)
        self.mette_a_jour(type_piece)
        try:
            with sq.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT factu, client, datee, montant 
                    FROM infov 
                    WHERE type_fact = ? AND statut != 'Validé' AND statut ='En cours'
                """, (type_piece,))
                lignes = cur.fetchall()

                for row_num, ligne in enumerate(lignes):
                    self.table.insertRow(row_num)

                    # Case à cocher
                    chk = QCheckBox()
                    widget = QWidget()
                    lay = QHBoxLayout(widget)
                    lay.addWidget(chk)
                    lay.setAlignment(chk, Qt.AlignmentFlag.AlignCenter)
                    lay.setContentsMargins(0, 0, 0, 0)
                    self.table.setCellWidget(row_num, 0, widget)

                    # Infos
                    for col, val in enumerate(ligne):
                        self.table.setItem(row_num, col + 1, QTableWidgetItem(str(val)))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des pièces : {e}")

    
    def valider_selection(self):
        type_piece = self.combo_type.currentText()
        nouveau_statut = self.combo_statut.currentText()

        if type_piece != "Selectionner le Type de Pièce":
            if nouveau_statut != "Selectionner le Statut":
                try:
                    
                    if nouveau_statut not in ["Validé","Annulée"]:
                        QMessageBox.warning(self, "Action refusée", "Vous ne pouvez valider que les pièces en cours.")
                        return
                    with sq.connect(self.db_path) as conn:
                        cur = conn.cursor()
                        total_validees = 0

                        for row in range(self.table.rowCount()):
                            widget = self.table.cellWidget(row, 0)
                            chk = widget.findChild(QCheckBox) if widget is not None else None
                            if chk and chk.isChecked():
                                item = self.table.item(row, 1)
                                if item is not None:
                                    num_piece = item.text()
                                    cur.execute("UPDATE infov SET statut = ? WHERE factu = ?", (nouveau_statut, num_piece))
                                    total_validees += 1

                        conn.commit()
                        self.charger_pieces()

                        QMessageBox.information(self, "Succès", f"{total_validees} pièce(s) mise(s) à jour avec le statut : {nouveau_statut}")

                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la validation : {e}")
            else:
                 QMessageBox.warning(self, "Validation", "Veuillez choisir un statut valide.")
        else:
            QMessageBox.warning(self, "Validation", "Veuillez choisir un type de pièce.")            


class AjoutClf(QDialog):
    def __init__(self, db_path,typ=None):
        super().__init__()
        self.type = typ
        self.db_path = db_path
        self.ui=Ui_clientoufour()
        self.ui.setupUi(self)
        self.cal =cal()
        self.ui.comboBox.setVisible(False)
        self.ui.label_2.setVisible(False)
        self.ui.ajoutfourn.clicked.connect(lambda :self.ajoucl())
        self.ui.pushButt.clicked.connect(lambda:self.close)
        self.ui.idenfifiantLineEdit.setText(str(self.cal.random_client()))
        self.contact()

    def contact(self):
        self.ui.contactLineEdit.setValidator(self.cal.contact_validator(self.ui.contactLineEdit))  
    #modif
    def ajoucl(self):
        try:
            conn = cal.connect_to_db(self.db_path)
            if conn is None:
                QMessageBox.warning(self, "Erreur", "Impossible de se connecter à la base de données.")
                return
            cur = conn.cursor()
            id=self.ui.idenfifiantLineEdit.text().strip()
            nom = self.ui.nomEtPrNomLineEdit.text().strip()
            nom = self.cal.nom_upper(nom)
            cont = self.ui.contactLineEdit.text().strip()
            adr = self.ui.adresseLineEdit.text().strip()
            ville = self.ui.lineEdit.text().capitalize()
            
            
            try:
                
                if id != "":
                    if nom != "":
                        if cont !="":
                            if ville !="":
                                if adr != "":
                                    aj_client = f""" INSERT INTO client (id,type, nom, cont,adr,ville) VALUES (?,?,?,?,?,?);                                        
                                                            """
                                    liste_client=(id,self.type,nom,cont,adr,ville)
                                    detect_client='''select * from client where cont=?'''
                                    donnee_client=cur.execute(detect_client,[cont])
                                    list_fourn=donnee_client.fetchall()
                                    if list_fourn:
                                        QMessageBox.warning(self,"ENREGISTREMENT",f"{self.ui.contactLineEdit.text()} existe dans votre liste de client.<br> Veuillez entrer un autre contact")
                                        self.ui.contactLineEdit.setFocus()
                                    else:
                                        msg = QMessageBox(self)
                                        msg.setWindowTitle("ENREGISTREMENT")
                                        msg.setText("Etes-vous sur de vouloir enregistrer ces données?")
                                        yes = msg.addButton("Oui",QMessageBox.ButtonRole.YesRole)
                                        non = msg.addButton("Non",QMessageBox.ButtonRole.NoRole)
                                        msg.exec()
                                        if msg.clickedButton() == yes:
                                            cur.execute(aj_client,liste_client)
                                            conn.commit()                             
                                            
                                        elif msg.clickedButton() == non:
                                            conn.rollback()
                                            QMessageBox.information(self, "ENREGISTREMENT", "Enregistrement annulé")
                        
                                        conn.close()
                                else:
                                    QMessageBox.warning(self,"ENREGISTREMENT","Adresse invalide ou vide")
                                    self.ui.adresseLineEdit.setFocus()
                            else:
                                QMessageBox.warning(self, "ENREGISTREMENT", "Ville invalide ou vide")
                                self.ui.lineEdit.setFocus()
                        else:
                            QMessageBox.warning(self, "ENREGISTREMENT", "Contact invalide ou vide")
                            self.ui.contactLineEdit.setFocus()
                    else:
                        QMessageBox.warning(self, "ENREGISTREMENT", "Nom ou prénom invalide ou vide")
                        self.ui.nomEtPrNomLineEdit.setFocus()
                else:
                    QMessageBox.warning(self, "ENREGISTREMENT", "Identifiant invalide ou vide")
                    self.ui.idenfifiantLineEdit.setFocus()
                
            except sq.OperationalError as e:
                
                QMessageBox.warning(self, "Erreur", f"{self.ui.idenfifiantLineEdit.text()} existe.<br>Veuiller entrer un autre contact.")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"{e}")
        except AttributeError as e:
            QMessageBox.warning(self, "Erreur", f"{e}")
           