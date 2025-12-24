# auteur: zongo soumaïla
# Tel: +226 56832442 / 70925613
from datetime import datetime
import os
import webbrowser
import logging
import locale

from fonction.valide import choixPiece
locale.setlocale(locale.LC_ALL, "")  # pour séparateur milliers si besoin
from fonction.model import Model
from PySide6.QtCore import Qt, QDateTime, QDir
from PySide6.QtWidgets import (
     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,QApplication,
    QLabel, QLineEdit, QDateTimeEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QDoubleSpinBox, QHeaderView, QMessageBox,QSizePolicy,
    QAbstractItemView, QProgressBar, QCompleter, QStyle, QCheckBox, QTableView,QInputDialog
)
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, QAction

from fonction.methode import Numeroteur, cal

STATUT_PIECE = {
    "Devis": ["En cours", "Validé", "Traité", "Annulée"],
    "Commande": ["En cours", "Validé", "Traité", "Annulée"],
    "Bon de livraison": ["En cours", "Validé", "Traité", "Annulée"],
    "Facture": ["En cours", "Validé", "Traité", "Annulée"]
}

log = logging.getLogger(__name__)

class Vente(QMainWindow):
    def __init__(self, dbfolder, current_user=None) -> None:
        super().__init__()
        
        self.setWindowIcon(QIcon(':/icon/icone.png'))
        
        screen = QApplication.primaryScreen()
        size = screen.availableGeometry()
        w = int(size.width() * 0.6)
        h = int(size.height() * 0.6)
        self.resize(w, h)
        
        # Centrer la fenêtre
        frame_geo = self.frameGeometry()
        center_point = screen.availableGeometry().center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.select_ = choixPiece()
        self.select_.exec()
        self.piece = self.select_.validateSelection()
        self.dbfolder = dbfolder
        self.conn = cal().connect_to_db(self.dbfolder)
        self.numeroteur = Numeroteur(self.dbfolder)
        self.Model = Model()
        self.cal = cal()
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)

        # --- Informations pièce + client ---
        top_h = QVBoxLayout()
        grp_piece = QGroupBox(f"Référence: {self.piece}")
        self.setWindowTitle(f"Création de pièce — {self.piece}")
        f1 = QHBoxLayout()
        self.date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_edit.setSizePolicy(sizePolicy2)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.num_line = QLineEdit("F-XXXX-YYY")
        self.num_line.setReadOnly(True)
        self.num_line.setStyleSheet("background:#f0f0f0;")

        self.num_line.setEnabled(False)
        self.num_line.setSizePolicy(sizePolicy2)
        self.status_line = QComboBox()
        self.status_line.setSizePolicy(sizePolicy2)
        f1.addWidget(QLabel("Date:")); f1.addWidget(self.date_edit)
        f1.addWidget(self.num_line)
        f1.addWidget(QLabel("Statut:")); f1.addWidget(self.status_line)
        grp_piece.setLayout(f1)

        grp_client = QGroupBox("Client / Remarque")
        f2 = QHBoxLayout()
        self.client_line = QLineEdit();self.client_line.setEnabled(False);self.client_line.setSizePolicy(sizePolicy2)
        self.remarque_line = QLineEdit()
        self.remarque_line.setSizePolicy(sizePolicy2)
        f2.addWidget(QLabel("Client:")); f2.addWidget(self.client_line)
        f2.addWidget(QLabel("Remarque:")); f2.addWidget(self.remarque_line)
        grp_client.setLayout(f2)

        top_h.addWidget(grp_client, 4)
        top_h.addWidget(grp_piece, 3)
        main.addLayout(top_h)

        # --- Selector article + add button ---
        add_h = QHBoxLayout()
        label = QLabel("Ajouter un article:")
        self.article_combo = QComboBox()
        
        self.article_combo.setEditable(False)
        add_h.addWidget(label)
        add_h.addWidget(self.article_combo,4 )
        main.addLayout(add_h)

        # --- Panier (table) ---
        grp_panier = QGroupBox("Panier")
        vpan = QVBoxLayout()
        self.table = QTableWidget(0, 6)
        self.table.setSizePolicy(sizePolicy2)
        self.table.setStyleSheet("selection-background-color: lightblue;")
        headers = ["Code", "Prot", "Quantité", "Prix Unitaire", "Montant", "Action"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        vpan.addWidget(self.table)
        grp_panier.setLayout(vpan)
        main.addWidget(grp_panier, 6)

        # --- Paiement / Totaux ---
        bot_h = QHBoxLayout()
        # Left - paiement
        left_g = QGroupBox("Paiement")
        left_l = QHBoxLayout()
        self.mode_paiement = QComboBox()
        self.tva_checkbox = QCheckBox("Appliquer TVA"); self.tva_checkbox.setCheckable(True)
        self.tva_spin = QDoubleSpinBox(); self.tva_spin.setValue(0.0); self.tva_spin.setSuffix(" %")
        left_l.addWidget(QLabel("Mode:")); left_l.addWidget(self.mode_paiement)
        left_l.addWidget(self.tva_checkbox); left_l.addWidget(self.tva_spin)
        left_g.setLayout(left_l)

        # Right - totals & progress
        right_g = QGroupBox("Montants")
        right_l = QVBoxLayout()
        row1 = QHBoxLayout()
        self.ht_label = QLabel("0.00")
        self.ht_label.setSizePolicy(sizePolicy2)
        self.ttc_label = QLabel("0.00")
        self.ttc_label.setSizePolicy(sizePolicy2)
        self.paid_spin = QDoubleSpinBox()
        self.paid_spin.setSizePolicy(sizePolicy2)
        self.paid_spin.setMinimum(0.0);self.paid_spin.setMaximum(999999999999); self.paid_spin.setDecimals(2)
        row1.addWidget(QLabel("Montant HT:")); row1.addWidget(self.ht_label,2)
        row1.addWidget(QLabel("Montant TTC:")); row1.addWidget(self.ttc_label,2)
        row1.addWidget(QLabel("Montant versé:")); row1.addWidget(self.paid_spin,2)
        right_l.addLayout(row1)
        # Progress bar and remainder
        self.progress = QProgressBar(); self.progress.setRange(0, 100)
        self.reste_label = QLabel("0.00")
        pb_row = QHBoxLayout()
        pb_row.addWidget(QLabel("Paiement:"),2); pb_row.addWidget(self.progress,2)
        pb_row.addWidget(QLabel("Reste:"),2); pb_row.addWidget(self.reste_label,2)
        right_l.addLayout(pb_row,2)
        right_g.setLayout(right_l)

        bot_h.addWidget(left_g, 3)
        bot_h.addWidget(right_g, 5)
        main.addLayout(bot_h)

        # setup completer/model for article_combo (table-like)
        self.article_model = QStandardItemModel()
        self.article_combo.setModel(self.article_model)

        # n'exécute pas exec_() en init — laisse la commande appelante gérer l'affichage
        self.current_user = current_user or "Admin"
        self.tau = self.cal.charger_tva_devise(self.dbfolder)

        # --- Liste des dépôts dans la toolbar si multi-dépôts ---
        
        # --- Liste des articles (table view popup) ---
        mon_modele = QStandardItemModel()
        self.article_combo.setModel(mon_modele)
        self.article_combo.setView(QTableView())
        self.combo = self.article_combo.view()
        if self.combo:
            self.combo.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.combo.setMinimumWidth(400)
            self.combo.setMinimumHeight(150)
            self.combo.setStyleSheet("background-color: white; color: black;")
            self.combo.setSizeAdjustPolicy(QAbstractItemView.SizeAdjustPolicy.AdjustToContents)

        # --- champs internes ---
        self.libelle = None
        self.code = None
        self.prix = None
        self.reste = 0.0
        self.net = 0.0
        self.id_clt = None
        self.nom_clt = None

        # --- config + init ---
        self.populate_accounts_combos()
        self.mette_a_jour(piece=self.piece)
        
        self.choix_()

        # autocomplete remarques
        data_list = self.get_data_remaeque() or []
        completer = QCompleter(data_list)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.remarque_line.setCompleter(completer)

        # Table des articles (ajout d'une colonne dépôt)
        self.tab = self.table
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Code", "Prot", "Quantité", "Prix Unitaire", "Montant", "Action"
        ])
        self.table.horizontalHeader().setStyleSheet("background-color: lightgray;")
        self.table.verticalHeader().setDefaultSectionSize(40)

        # connexions
        self.tva_spin.valueChanged.connect(self.mnt_ttc)
        self.paid_spin.valueChanged.connect(self.mnt_ttc)
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.article_combo.activated.connect(lambda index: self.combo_article_selected(index))
        self.mode_paiement.activated.connect(lambda: self.type_paiement())
        self.tva_checkbox.stateChanged.connect(lambda: self.validateSelection())

        # charger articles pour dépôt par défaut
        self.liste_deroulante()

        tb = self.addToolBar("Actions")

        act_validate = QAction(QIcon.fromTheme("document-save", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)), "Valider", self)
        act_print = QAction(QIcon.fromTheme("document-print", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)), "Imprimer", self)
        act_new = QAction(QIcon.fromTheme("list-add", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)), "Nouvelle pièce", self)
        act_client =  QAction(QIcon(":/icon/300.png"), "Sélection du client", self)
       
        tb.addAction(act_client)
        tb.addAction(act_validate)
        tb.addAction(act_print)
        tb.addAction(act_new)
        
        act_client.triggered.connect(lambda: self.id_client())
        act_validate.triggered.connect(lambda: self.list_vente())
        act_new.triggered.connect(lambda: self.new_facture())  
        
    
    def genere_numero_facture(self):
        annee = datetime.now().year
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            return False
        cur = conn.execute("""
                            SELECT COUNT(*) FROM infov WHERE strftime('%Y',datee)=?
                            """,(str(annee),))
        compteur = cur.fetchone()[0] + 1
        if self.piece == "Devis":
            return f"DV-{annee}-{compteur:04d}"
        elif self.piece =="Commande":
            return f"COM-{annee}-{compteur:04d}"
        elif self.piece == "Bon de livraison":
            return f"BLV-{annee}-{compteur:04d}"
        else:
            return f"FAC-{annee}-{compteur:04d}"

    def id_client(self):
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            return
        cur = conn.cursor()
        row = cur.execute("SELECT id, nom FROM client WHERE type ='Client' ").fetchall()
        liste_clients = [f"{id_}_{nom}" for id_,nom in row]
        select_clien, ok = QInputDialog.getItem(self,"Sélectionner un client","CLIENTS",liste_clients,0,False)
        if ok:
            self.id_clt,self.nom_clt = select_clien.split("_",1)
            self.client_line.setText(str(self.nom_clt))


    def liste_deroulante(self):
        """Remplit la liste d'articles en fonction du dépôt choisi (ou dépôt principal)."""
        try:
            conn = self.cal.connect_to_db(self.dbfolder)
            if conn is None:
                return
            cur = conn.cursor()            
            query = '''
                SELECT p.name, s.id_libelle, s.price_vente 
                FROM stock s LEFT JOIN products p ON p.ref = s.id_libelle
                WHERE s.qty > 0
            '''
            cur.execute(query)
            rows = cur.fetchall()
            conn.close()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Prod", "Code", "Prix Unitaire"])
            for row in rows:
                items = [QStandardItem(str(col)) for col in row]
                model.appendRow(items)

            self.article_combo.setModel(model)
        except Exception as e:
            log.error("Erreur DB dans liste_deroulante: %s", e)

    def get_data_remaeque(self):
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            return []
        cur = conn.cursor()
        cur.execute("SELECT remarque FROM infov")
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_statut(self, piece: str):
        return STATUT_PIECE.get(piece, [])

    def mette_a_jour(self, piece):
        self.status_line.clear()
        self.status_line.addItems(self.get_statut(piece))

    def choix_(self):
        text_ = self.piece
        if text_ == "Devis":
            self.num_line.setText(str(self.numeroteur.preview("DV")))
            # self.num_line.setText(str(self.cal.numero_devi_pro()))
        elif text_ == "Commande":
            self.num_line.setText(str(self.numeroteur.preview("CM")))
        elif text_ == "Bon de livraison":
            self.num_line.setText(str(self.numeroteur.preview("BL")))
        elif text_ == "Facture":
            self.num_line.setText(str(self.numeroteur.preview("FAC")))
        else:
            QMessageBox.information(self, "Document", "Option inconnue")

    def validateSelection(self):
        if self.tva_checkbox.isChecked():
            if self.tau:
                self.tva_spin.setValue(float(self.tau.get('tva', 0)))
            self.tva_spin.setEnabled(True)
        else:
            self.tva_spin.setEnabled(False)
            self.tva_spin.setValue(0)

    def combo_article_selected(self, index):
        """Ajoute l'article sélectionné dans la table si stock dispo."""
        try:
            model = self.article_combo.model()
            if not model or index < 0:
                return

            # lire infos article
            libelle = model.index(index, 0).data()
            code = model.index(index, 1).data()
            prix = float(model.index(index, 2).data())

            quantite_depot = self.get_stock_dispo(code)
            if self.piece == "Facture":
                if quantite_depot < 1:
                    QMessageBox.warning(
                        self,
                        "Stock insuffisant",
                        f"L'article '{libelle}' (code {code}) n'a pas de stock disponible dans ce dépôt.\n"
                        f"Stock disponible : {quantite_depot} unité(s)."
                    )
                    return
            
            if self.cal.verifi_exit(self.tab, code) is False:
                row = self.tab.rowCount()
                self.tab.insertRow(row)
                qt_spin = QDoubleSpinBox()
                qt_spin.setMinimum(0)
                qt_spin.setMaximum(9999999999)
                qt_spin.setValue(1.0)
                qt_spin.valueChanged.connect(self.upd_value_cel)
                prix_spin = QDoubleSpinBox()
                prix_spin.setMinimum(0)
                prix_spin.setMaximum(9999999999)
                prix_spin.setValue(prix)
                prix_spin.valueChanged.connect(self.upd_value_cel)
                montant = 1 * prix
                # bouton supprimer (lié à la ligne)
                btn = QPushButton("Supprimer")
                btn.setStyleSheet("background-color: transparent;border: none; color: red;")
                btn.clicked.connect(lambda _, r=row: self.remove_row(r))
                # remplir ligne
                self.tab.setItem(row, 0, QTableWidgetItem(code))
                self.tab.setItem(row, 1, QTableWidgetItem(libelle))
                self.tab.setCellWidget(row, 2, qt_spin)
                self.tab.setCellWidget(row, 3, prix_spin)
                self.tab.setItem(row, 4, QTableWidgetItem(f"{montant:.2f}"))
                self.tab.setCellWidget(row, 6, btn)

                self.somme_vente()
            else:
                QMessageBox.information(self, "Ajout article", f"L'article '{code}' existe déjà dans la liste.")
        except Exception as e:
            log.error("Erreur combo_article_selected: %s", e)
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter l'article.\n{e}")



    def get_stock_dispo(self, code):
        try:
            conn = self.cal.connect_to_db(self.dbfolder)
            if conn is None:
                return 0
            cur = conn.cursor()
            cur.execute("SELECT IFNULL(quantite,0) FROM stock WHERE id_libelle=?", (code))
            res = cur.fetchone()
            conn.close()
            return res[0] if res and res[0] is not None else 0
        except Exception:
            return 0

    def remove_row(self, row_index: int):
        try:
            if row_index < 0 or row_index >= self.tab.rowCount():
                QMessageBox.warning(self, 'Avertissement', 'Ligne invalide.')
                return
            msg = QMessageBox(self)
            msg.setWindowTitle("SUPPRESSION")
            msg.setText("Êtes-vous sûr de vouloir retirer cette ligne ?")
            yes = msg.addButton("Oui", QMessageBox.ButtonRole.YesRole)
            non = msg.addButton("Non", QMessageBox.ButtonRole.NoRole)
            msg.exec()
            if msg.clickedButton() == yes:
                self.tab.removeRow(row_index)
                self.somme_vente()
        except Exception as e:
            log.error(f"Erreur remove_row: {e}")

    def upd_value_cel(self):
        try:
            index = self.tab.currentIndex().row()
            if index < 0:
                # Si pas de ligne sélectionnée on recalculera tous les montants
                pass
            # recalculer le montant de la ligne courante (ou de toutes)
            for row in range(self.tab.rowCount()):
                prix_widget = self.tab.cellWidget(row, 3)
                qte_widget = self.tab.cellWidget(row, 2)
                if prix_widget is None or qte_widget is None:
                    continue
                prix = float(prix_widget.value())
                qte = float(qte_widget.value())
                new_mnt = prix * qte
                self.tab.setItem(row, 4, QTableWidgetItem(f"{new_mnt:.2f}"))

            # recalcul total
            total_sum = 0.0
            for row in range(self.tab.rowCount()):
                mnt_item = self.tab.item(row, 4)
                if mnt_item:
                    try:
                        total_sum += float(mnt_item.text())
                    except ValueError:
                        continue
            self.ht_label.setText(f"{total_sum:.2f}")
            self.somme_vente()
        except Exception as e:
            log.error(f"upd_value_cel error: {e}")

    def somme_vente(self):
        total_sum = 0.0
        for row in range(self.tab.rowCount()):
            mnt = self.tab.item(row, 4)
            if mnt is not None:
                try:
                    total_sum += float(mnt.text())
                except ValueError:
                    log.warning(f"Valeur non numérique dans le montant de la ligne {row}:{mnt.text()}")
                    continue
        self.ht_label.setText(f"{total_sum:.2f}")
        self.mnt_ttc()

    def reste_(self, total: float, pay: float):
        pd = total - pay
        if pd < 0.0:
            pd = 0.0
        return pd

    def mnt_ttc(self):
        try:
            mnt_ht = float(self.ht_label.text()) if self.ht_label.text() else 0.0
        except ValueError:
            mnt_ht = 0.0
        va_aj = self.tva_spin.value()
        e_mntpy = self.paid_spin.value()
        net = round(float(mnt_ht * (1 + (va_aj / 100.0))), 2)
        reste = round(max(net - e_mntpy, 0.0), 2)

        # formatage
        self.ttc_label.setText(f"{net:.2f}")
        self.reste_label.setText(f"{reste:.2f}")

        # progression paiement en pourcentage
        percent = 0
        if net > 0:
            percent = int(min(max((e_mntpy / net) * 100, 0), 100))
        self.progress.setValue(percent)

    def statut(self, net: float, verse: float):
        reste = round((net - verse), 2)
        if reste == 0:
            return "Payé"
        elif 0 < verse < net:
            return "Avance"
        elif verse == 0:
            return "Impayé"
        else:
            return "Payé"

    def populate_accounts_combos(self):
        """Remplit les status_line des comptes des la base de données."""
        fichier_json = self.cal.load_json()
        try:
            self.mode_paiement.clear()
            # garder 1ère option neutre
            self.mode_paiement.addItem("Moyen de paiement", None)
            for num in fichier_json:
                libelle = num.get("libelle")
                compte = num.get("compte")
                self.mode_paiement.addItem(libelle, compte)
        except Exception as e:
            QMessageBox.critical(self, "Erreur SQL", f"Erreur lors du chargement des moyen de paiement: {e}")

    def Liste_donne(self):
        # texte = self.texte.get_clt()
        id_clt=self.id_clt; nmclt = self.nom_clt
        factu = self.num_line.text()
        dat = self.date_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        dat = datetime.strptime(dat, "%Y-%m-%d %H:%M")
        mnt_ht = float(self.ht_label.text()) if self.ht_label.text() else 0.0
        e_mntpy = self.paid_spin.value()
        va_aj = self.tva_spin.value()
        mnt_ttc = round(float(mnt_ht * (1 + (va_aj / 100))), 2)
        e_reste = self.reste_(mnt_ttc, e_mntpy)
        remarque = self.remarque_line.text()
        piece = self.piece
        e_mntpy = self.paid_spin.value()
        net_payer = float(self.ttc_label.text()) if self.ttc_label.text() else 0.0
        etat = self.statut(net_payer, e_mntpy)

        if piece == "Facture":
            lis_fact = [factu, id_clt, mnt_ht, mnt_ttc, e_mntpy, e_reste, dat, etat, piece, remarque,self.current_user]
        else:
            lis_fact = [factu, id_clt, mnt_ht, mnt_ttc, 0.0, 0.0, dat, self.status_line.currentText(), piece, remarque,self.current_user]

        return lis_fact

    def type_paiement(self):
        moyen_paiem = self.mode_paiement.currentText()
        moyen = self.cal.code_paiement(moyen_paiem)
        facture = self.num_line.text()
        moyen_ = f"{moyen}-{facture}"
        return moyen_

    def get_data_by(self):
        id_clt=self.id_clt; nmclt = self.nom_clt
        factu = self.num_line.text()
        dat = self.date_edit.date().toString("yyyy-MM-dd")
        dat = datetime.strptime(dat, "%Y-%m-%d")
        data_vente = {"line_items": []}
        for row in range(self.table.rowCount()):
            if not self.table.item(row, 0):
                continue

            code_item = self.table.item(row, 0)
            if code_item is None:
                continue
            code = code_item.text()
            prd_item = self.table.item(row, 1)
            if prd_item is None:
                continue
            prd = prd_item.text()
            qte = float(self.table.cellWidget(row, 2).value())
            pri = float(self.table.cellWidget(row, 3).value())
            mnt_item = self.table.item(row, 4)
            mnt = float(mnt_item.text()) if mnt_item is not None else pri * qte

            
            row_data = [nmclt, code, factu, prd, pri, qte, mnt, dat, id_clt]
            data_vente["line_items"].append(row_data)

        return data_vente

    def _validate_inputs(self) -> bool:
        """Vérifie que toutes les conditions de saisie sont remplies"""
        nmclt = self.nom_clt

        if self.table.rowCount() <= 0:
            QMessageBox.warning(self, "ENREGISTREMENT", "Aucun article. Veuillez ajouter des produits !")
            return False
        if not self.piece or self.piece == "Pièces":
            QMessageBox.warning(self, "ENREGISTREMENT", "Type de pièce non reconnu.")
            return False
        if nmclt == "" or None:
            QMessageBox.warning(self, "ENREGISTREMENT", "Veuillez sélectionner un client.")
            return False
        return True

    def _save_facture(self, cur, L, data_vente):
        """Traitement spécifique pour une facture"""
        refe = self.type_paiement()
        id_clt=self.id_clt; nmclt = self.nom_clt
       
        montant_ht_total = 0.0
        numero_facture = self.num_line.text()
        date_emission = datetime.strptime(self.date_edit.date().toString("yyyy-MM-dd"), "%Y-%m-%d")

        # Insérer chaque ligne et mettre à jour le stock (par dépôt)
        for e in data_vente.get("line_items", []):
            cd = e[1]  # code article
            qte = e[5]
            prix_unitaire = e[4]
            montant_ht_total += prix_unitaire * qte

            cur.execute(
                """INSERT INTO vent (client, code, facture, libelle, prix, quantite,
                                    montant, datee, id_clt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])
            )

            # # Mise à jour du stock pour le dépôt précis
            cur.execute(
                "UPDATE stock SET qty = qty - ? WHERE  id_libelle = ?",
                (qte, cd)
            )

        

        if L[7] in ("Payé", "Avance"):
            if self.mode_paiement.currentText() != "Moyen de paiement":
               
                self.cal.insert_tresorerie(cur, date_emission, "Vente " + numero_facture, montant_ht_total, "ENTREE", self.mode_paiement.currentText(), self.current_user)
                if self.mode_paiement.currentText() == "Espèces":
                    typ_compte = "Caisse"
                elif self.mode_paiement.currentText() == "Mobile money":
                    typ_compte = "Compte Mobile"
                else:
                    typ_compte = "Banque"
                # insertion trésorerie simplifiée
                self.cal.insert_tresorerie(cur, date_emission, "Vente " + numero_facture, montant_ht_total, "ENTREE", typ_compte, self.current_user)
            else:
                QMessageBox.warning(self, "Mode de paiement", "Sélectionnez un mode de paiement valide")
                self.mode_paiement.setFocus()
                return
       
            

        # Insertion dans infov
        cur.execute(
            """INSERT INTO infov (factu, client, montant, mnt_ttc, payer, monn, datee,
                                statut, type_fact, remarque, utilisateur)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            L + [self.current_user]
        )

       

    def safe_execution(func):
        """Décorateur pour capturer les erreurs et afficher un QMessageBox"""
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                log.exception("Erreur: %s", e)
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")
                return None
        return wrapper

    def _save_devis_commande(self, cur, L, data_vente):
        """Traitement pour devis ou commande"""
        for e in data_vente.get("line_items", []):
            cur.execute(
                """INSERT INTO liste (client,code,facture,libelle,prix,quantite,montant,datee,id_clt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])
            )

        cur.execute(
            """INSERT INTO infov (factu, client, montant, mnt_ttc, payer, monn, datee,
                                statut, type_fact, remarque, utilisateur)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            L
        )
    def save_fact_vente(self, cur, data_vente, L, numero_facture):
        montant_ht_total = 0.0
        date_emission = datetime.strptime(self.date_edit.date().toString("yyyy-MM-dd"), "%Y-%m-%d")
        
        # 1. Insertion des lignes de vente et mise à jour du stock
        for e in data_vente["line_items"]:
            cd, qte, pri, id_depot = e[1], e[5], e[4], e[9]
            montant_ht_total += pri * qte

            # Insertion de la ligne dans la table 'vent'
            cur.execute(
                """INSERT INTO vent (client, code, facture, libelle, prix, quantite,
                                    montant, datee, id_clt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])
            )

            # Mise à jour du stock pour le dépôt précis
            cur.execute(
                "UPDATE stock SET quantite = quantite - ? WHERE code_article = ? AND id_depot = ?",
                (qte, cd, id_depot)
            )

        # 2. Préparation de la comptabilité
        montant_ttc = L[3] # L[3] contient le montant TTC
        
        
        # 3. Traitement du paiement et de la trésorerie (si payé/avance)
        if L[7] in ("Payé", "Avance"):
            compte_paiement = self.mode_paiement.currentData()
            if compte_paiement is None:
                QMessageBox.warning(self, "Mode de paiement", "Sélectionnez un mode de paiement valide pour l'encaissement.")
                # Lancer une exception annulera la transaction grâce au décorateur safe_execution
                raise ValueError("Mode de paiement non sélectionné pour une facture payée/avancée.")
            
            # Insertion trésorerie simplifiée (pour le module de gestion de trésorerie)
            typ_compte = self.mode_paiement.currentText()
            typ_compte = "Caisse" if typ_compte == "Espèces" else "Compte Mobile" if typ_compte == "Mobile money" else "Banque"
            self.cal.insert_tresorerie(cur, date_emission, "Vente " + numero_facture, montant_ttc, "ENTREE", typ_compte, self.current_user)

        # 4. Insertion dans infov (en-tête de la pièce)
        cur.execute(
            """INSERT INTO infov (factu, client, montant, mnt_ttc, payer, monn, datee,
                                statut,  type_fact, remarque, utilisateur)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            L
        )

    @safe_execution
    def list_vente(self):
        """Enregistre les données de vente avec utilisateur courant"""
        if not self._validate_inputs():
            return
        # 🔐 Génération OFFICIELLE du numéro
        if self.piece == "Facture":
            numero = self.numeroteur.generer("FAC")
        elif self.piece == "Bon de livraison":
            numero = self.numeroteur.generer("BL")
        elif self.piece == "Commande":
            numero = self.numeroteur.generer("CM")
        elif self.piece == "Devis":
            numero = self.numeroteur.generer("DV")
        else:
            QMessageBox.warning(self, "Erreur", "Type de pièce inconnu")
            return

        # 🔒 On verrouille le numéro
        self.num_line.setText(numero)
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            QMessageBox.critical(self, "Erreur BD", "Impossible de se connecter à la base de données.")
            return
        L = self.Liste_donne()
        data_vente = self.get_data_by()
        if not data_vente:
            QMessageBox.warning(self, "Données Manquantes", "Aucune donnée de vente disponible.")
            return

        with conn:
            cur = conn.cursor()
            if self.piece == "Facture":
                self._save_facture(cur, L, data_vente)
            else:
                self._save_devis_commande(cur, L, data_vente)

        QMessageBox.information(self, "Succès", f"{self.piece} : {self.num_line.text()} enregistrée par {self.current_user}.")

    def new_facture(self):
        self.table.setRowCount(0)
        self.ht_label.setText("0.00")
        self.paid_spin.setValue(0.00)
        self.tva_spin.setValue(0.00)
        self.num_line.clear()

    def Info(self, factu):
        try:
            var_dic_vente = {}
            conn = self.cal.connect_to_db(self.dbfolder)
            if conn is None:
                return
            cur = conn.cursor()
            pr_v = '''SELECT * from infov where factu=?'''
            cur.execute(pr_v, [factu])
            cv = cur.fetchone()
            if cv:
                self.tva = float(cv[9]) if len(cv) > 9 else 0.0
                self.date = cv[6] if len(cv) > 6 else ""
                self.facto = cv[0]
                self.montant_verse = cv[4]
                self.reste = cv[5]
                self.type_fact = cv[9] if len(cv) > 9 else ""
                self.remarque = cv[11] if len(cv) > 11 else ""
                info = '''SELECT nom,cont,adr,ville from client where id=?'''
                cur.execute(info, [cv[1]])
                info_clt = cur.fetchone()
                if info_clt:
                    self.nom_clt = info_clt[0]
                    self.contact1 = info_clt[1]
                    self.adresse1 = info_clt[2]
                    self.ville = info_clt[3]

                var_dic_vente = {"Adrresse": self.adresse1,
                                 "Contact": self.contact1,
                                 "date": self.date,
                                 "facture": self.facto,
                                 "tva": self.tva,
                                 "ville": self.ville,
                                 "nom": self.nom_clt,
                                 "mont_verse": self.montant_verse,
                                 "reste": self.reste,
                                 "type_facture": self.type_fact,
                                 "remarque": self.remarque
                                 }
                conn.close()
            else:
                QMessageBox.warning(self, "Erreur", "Veuillez d'abord enregistrer la pièce")
            return var_dic_vente
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)} dans Info")
            QMessageBox.warning(self, "Erreur", f"{e} dans Info")
# 

# --- fin de la classe VentePiece ---