# auteur: zongo soumaïla
# Tel: +226 54267778 / 70925613


import datetime
import os
from jinja2 import Environment, FileSystemLoader
# from compta.accounting_logic import generer_ecritures_paiement_vente
# from compta.ecriture import AccountingDashboard
from fonction.model import Model
from piece.detail import Details
from piece.compl import  DialogueConversion, ValidationPieces
from interface.credit_ui import Ui_Ui_payereste
from PySide6.QtCore import  QDate,QDir,Qt,QDateTime
from PySide6.QtGui import QAction,QIcon
from PySide6.QtWidgets import (QTableWidgetItem,QTableWidget,QDateEdit,QHeaderView, 
                               QMessageBox,QDialog,QMenu,QFrame, 
                               QWidget,QComboBox,QVBoxLayout, 
                               QHBoxLayout,QLineEdit,QLabel, QPushButton)


import webbrowser
try:
    from num2words import num2words
except Exception:
    # num2words non installé — fonctionnalité optionnelle
    num2words = None
import logging.config
import sqlite3 as sq
import pandas as pd
from fonction.methode import Numeroteur, cal
from piece.vente import Vente
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

# Configurez Jinja2 pour qu'il cherche les modèles dans ce dossier
env = Environment(loader=FileSystemLoader('template'))

class ListePiece(QWidget):
    def __init__(self, dbfolder: str):
        super().__init__()
        self.setWindowIcon(QIcon(':/icon/icone.png'))
        self.dbfolder = dbfolder
        self.numeroteur = Numeroteur(self.dbfolder)
        self.page_size = 50  # Nombre de lignes par page
        self.current_page = 0
        self.cached_data = []  # Cache des données
        self.cal = cal()
        charge_devise = None
        try:
            charge_devise = self.cal.charger_tva_devise(self.dbfolder)
        except Exception:
            log.warning("Impossible de charger la devise/tva, valeur par défaut utilisée")
        # Configuration par défaut si non trouvée
        self.devise = charge_devise["devise"] if charge_devise else "CFA"
        self.Model = Model()

        # colonnes et indices (constantes locales)
        self.cols = [
            "N°Facture", "ID Client", "Mnt HT", "Mnt TTC",
            "Mnt versé", "Mnt restant", "Statut",
            "Date", "Pièce", "Source", "User"
        ]
        (self.COL_FACTURE, self.COL_CLIENT, self.COL_MONTANT_HT, self.COL_MONTANT_TTC,
         self.COL_VERSE, self.COL_RESTANT, self.COL_STATUT,
         self.COL_DATE, self.COL_PIECE, self.COL_SOURCE, self.COL_USER) = range(len(self.cols))

        self.toolbars = []
        self.user = None

        self.ini()

        
    def ini(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        box_h = QHBoxLayout()    
        btn_add = QPushButton("Ajouter Pièce")    
        btn_add.setIcon(QIcon(":/icon/add (1).png"))
        btn_add.setToolTip("Ajouter une nouvelle pièce")
        btn_add.clicked.connect(lambda: self.open_window())
        btn_add.setObjectName("PrimaryButton")
        btn_valider = QPushButton("Valider Pièce")
        btn_valider.setIcon(QIcon(":/icon/updated.png"))
        btn_valider.setToolTip("Valider la pièce sélectionnée")
        btn_valider.setObjectName("PrimaryButton")
        btn_valider.clicked.connect(lambda: self.open_liste_valide())

        btn_transformer = QPushButton("Transformer une Pièce")
        btn_transformer.setIcon(QIcon(":/icon/262.png"))
        btn_transformer.setToolTip("Transformer une pièce en une autre")
        btn_transformer.setObjectName("PrimaryButton")
        btn_transformer.clicked.connect(lambda: self.open_conver())

        btn_supprimer = QPushButton("Supprimer")
        btn_supprimer.setIcon(QIcon(":/icon/remove (4).png"))
        btn_supprimer.setToolTip("Supprimer la pièce sélectionnée")
        btn_supprimer.setObjectName("DangerButton")
        btn_supprimer.clicked.connect(self.delete_fact_vent)

        btn_imprimer = QPushButton("Imprimer")
        btn_imprimer.setIcon(QIcon(":/icon/fileprint.png"))
        btn_imprimer.setToolTip("Imprimer la ligne sélectionnée")
        btn_imprimer.setObjectName("IconButton")
        btn_imprimer.clicked.connect(lambda: self.imprimerList_1())

        btn_rgler = QPushButton("Régler Facture")
        btn_rgler.setIcon(QIcon(":/icon/facturer.png"))
        btn_rgler.setToolTip("Régler la facture sélectionnée")
        btn_rgler.setObjectName("PrimaryButton")
        btn_rgler.clicked.connect(self.credivente)

        btn_refresh = QPushButton("Actualiser")
        btn_refresh.setIcon(QIcon(":/icon/refresh.png"))
        btn_refresh.setToolTip("Rafraîchir les données")
        btn_refresh.setObjectName("IconButton")
        btn_refresh.clicked.connect(self.refresh)

        box_h.addWidget(btn_add)
        box_h.addWidget(btn_valider)
        box_h.addWidget(btn_transformer)
        box_h.addWidget(btn_supprimer)
        box_h.addWidget(btn_imprimer)
        box_h.addWidget(btn_rgler)
        box_h.addWidget(btn_refresh)
        layout.addLayout(box_h)

        # barre de recherche et filtres
        top_layout = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Recherche Réfe ou ID Client ou Statut")
        self.search.setFixedWidth(220)
        labe_debut = QLabel("Période du ")
        date_debut = QDateEdit()
        date_debut.setCalendarPopup(True)
        date_debut.setDisplayFormat("yyyy-MM-dd")
        self.date = QDate.currentDate()
        date_debut.setDate(self.date)
        labe_au = QLabel("-au-")
        labe_au.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_fin = QDateEdit()
        date_fin.setCalendarPopup(True)
        date_fin.setDisplayFormat("yyyy-MM-dd")
        date_fin.setDate(self.date)
        labe_clt = QLabel("Client")
        self.liste_clt_combo = QComboBox()
        self.liste_pice = QComboBox()
        self.liste_pice.addItems(["Liste Pièces", "Devis", "Commande", "Bon de livraison", "Facture"])
        
        top_layout.addWidget(self.search)
        top_layout.addWidget(self.liste_pice)
        top_layout.addWidget(labe_debut)
        top_layout.addWidget(date_debut)
        top_layout.addWidget(labe_au)
        top_layout.addWidget(date_fin)
        top_layout.addWidget(labe_clt)
        top_layout.addWidget(self.liste_clt_combo)

        layout.addLayout(top_layout)

        # QTableWidget
        self.table = QTableWidget()
        self.table.setFrameShape(QFrame.Shape.Box) 
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setDefaultSectionSize(200)
        self.table.setColumnCount(len(self.cols))
        self.table.setHorizontalHeaderLabels(self.cols)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # initialiser listes et filtres
        self.full_rows = []
        self.search.textChanged.connect(self.filter_local)
        self.liste_pice.currentTextChanged.connect(self.filter_pice)
        self.liste_clt_combo.activated.connect(self.filter_local)
        date_debut.dateChanged.connect(lambda: self.filtre_date(date_debut.date(), date_fin.date()))
        date_fin.dateChanged.connect(lambda: self.filtre_date(date_debut.date(), date_fin.date()))

        # charger clients et rafraîchir
        self.liste_clt()
        self.refresh()
    
    def open_window(self):
        self.wind_piece = Vente(self.dbfolder,current_user="admin")
        self.wind_piece.show()
    # --- afficher pieces ---
    def show_context_menu(self, position):
        menu = QMenu()
        edit_action = QAction(QIcon(":/icon/facturer.png"), "Paiement", self)
        edit_avoir_action = QAction(QIcon(":/icon/262.png"), "Créer Avoir", self)
        delete_action = QAction(QIcon.fromTheme("edit-delete") or QIcon(":/icon/delete.png"), "Supprimer", self)
        duplicate_action = QAction(QIcon.fromTheme("printer") or QIcon(":/icon/fileprint.png"), "Imprimer", self)
        actionImprimerListe = QAction(QIcon.fromTheme("document-print"), "Imprimer Liste", self)
        edit_action.triggered.connect(self.credivente)
        delete_action.triggered.connect(self.delete_fact_vent)
        duplicate_action.triggered.connect(self.imprimerList_1)
        actionImprimerListe.triggered.connect(self.imprimer_liste_pieces)
        edit_avoir_action.triggered.connect(self.creer_avoir_depuis_facture)
        menu.addAction(edit_action)
        menu.addAction(edit_avoir_action)
        menu.addAction(delete_action)
        menu.addAction(duplicate_action)
        menu.addAction(actionImprimerListe)
        menu.exec(self.table.viewport().mapToGlobal(position))
    # populer la table avec les résultats filtrés
    def populate_table(self, filtered_data):
        self.table.setRowCount(0)
        for a in filtered_data:
            row = [a.get("N°Facture"), a.get("ID Client"), a.get("Montant HT"), a.get("Montant TTC"), 
                a.get("Montant versé"), a.get("Montant restant"), a.get("Statut"), 
                a.get("Date"), a.get("Pièce"), a.get("Source"), a.get("User")]
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate(row):
                if c in [self.COL_MONTANT_HT, self.COL_MONTANT_TTC, self.COL_VERSE, self.COL_RESTANT]:
                    val_ = self.format_montant(val)
                else:
                    val_ = str(val)
                self.table.setItem(r, c, QTableWidgetItem(val_))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def format_montant(self, val):
        """Formate un montant avec séparateur de milliers et devise."""
        try:
            # Suppose que la méthode dans cal.py est 'separateur_milier' (corrigez si nécessaire)
            if hasattr(self.cal, 'separateur_milieur'):
                return f"{self.cal.separateur_milieur(val)} {self.devise}"
            else:
                return f"{val} {self.devise}"  # Fallback si méthode manquante
        except Exception:
            return f"{val} {self.devise}"

    def filtre_date(self, start_date: QDate, end_date: QDate):
        filtered_data = self.get_all_pice()
        start = start_date.toString("yyyy-MM-dd")
        end = end_date.toString("yyyy-MM-dd")
        filtered_data = [item for item in filtered_data if start <= item.get("Date", "") <= end]
        self.populate_table(filtered_data)
    # --- obtenir toutes les pieces ---
    def get_all_pice(self):
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT factu, client, montant, mnt_ttc, payer, monn, statut,datee, type_fact,origine, utilisateur FROM infov ORDER BY datee DESC")
            rows = cur.fetchall()
            cols = ["N°Facture", "ID Client", "Montant HT", "Montant TTC", "Montant versé", "Montant restant",  "Statut", "Date", "Pièce",  "Source","Users"]
            row_zip = [dict(zip(cols, r)) for r in rows]
            return row_zip
        except Exception as e:
            log.error(f"Erreur get_all_pice: {e}", exc_info=True)
            return []
        finally:
            conn.close()

    # --- rafraîchissement table clients ---
    def liste_clt(self):
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            log.error("Impossible de se connecter à la BDD dans liste_clt")
            return
        try:
            cur = conn.cursor()
            sql = 'SELECT id_clt, client FROM vent GROUP BY id_clt'
            cur.execute(sql)
            data = cur.fetchall()
            self.liste_clt_combo.clear()
            i = 0
            for item in data:
                i += 1
                self.liste_clt_combo.addItem(f"{i}-{item[0]} {item[1]}", userData=item[0])
        except Exception as e:
            log.error(f"Erreur liste_clt: {e}", exc_info=True)
        finally:
            conn.close()

    # --- rafraîchissement table articles ---
    def refresh(self):
        # Charge seulement la page actuelle
        pices = self.get_all_pice()
        self.cached_data = pices  # Met à jour le cache
        self.full_rows = []  # Réinitialise pour la page
        self.table.setRowCount(0)
        for a in pices:
            row = [a.get("N°Facture"), a.get("ID Client"), a.get("Montant HT"), a.get("Montant TTC"), 
                a.get("Montant versé"), a.get("Montant restant"), a.get("Statut"), 
                a.get("Date"), a.get("Pièce"), a.get("Source"), a.get("User")]
            self.full_rows.append(row)
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate(row):
                if c in [self.COL_MONTANT_HT, self.COL_MONTANT_TTC, self.COL_VERSE, self.COL_RESTANT]:
                    val_ = self.format_montant(val)
                else:
                    val_ = str(val)
                self.table.setItem(r, c, QTableWidgetItem(val_))
        self.table.horizontalHeader().setDefaultSectionSize(200)
    # --- filtre local ---
    def filter_local(self, txt):
        t = str(txt).strip().lower()
        self.table.setRowCount(0)
        for row in self.full_rows:
            matches = False
            for c, val in enumerate(row):
                val_str = str(val).lower()
                if t in val_str:
                    matches = True
                    break
                # Pour les colonnes de montants, comparez numériquement (en supprimant les espaces et devise)
                if c in [self.COL_MONTANT_HT, self.COL_MONTANT_TTC, self.COL_VERSE, self.COL_RESTANT]:
                    try:
                        # Supprimez espaces, devise et comparez
                        clean_val = str(val).replace(' ', '').replace(self.devise, '').strip()
                        if t in clean_val or (t.isdigit() and float(clean_val) == float(t)):
                            matches = True
                            break
                    except ValueError:
                        pass  # Ignore si pas un nombre
            if matches:
                r = self.table.rowCount()
                self.table.insertRow(r)
                for c, val in enumerate(row):
                    if c in [self.COL_MONTANT_HT, self.COL_MONTANT_TTC, self.COL_VERSE, self.COL_RESTANT]:
                        val_ = self.format_montant(val)  # Utilise la méthode ci-dessus
                    else:
                        val_ = str(val)
                    self.table.setItem(r, c, QTableWidgetItem(val_))
    def show_lots_table(self, data):
        # Affiche les lots dans la table actuelle (remplace le contenu)
        self.table.setRowCount(len(data))
        for row, lot in enumerate(data):
            for col, value in enumerate(lot):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def filter_pice(self, txt):
        t = txt.strip().lower()
        self.table.setRowCount(0)
        for row in self.full_rows:
            if t == "" or t in str(row[self.COL_PIECE]).lower():
                r = self.table.rowCount(); self.table.insertRow(r)
                for c, val in enumerate(row):
                    self.table.setItem(r, c, QTableWidgetItem(str(val)))

    # ================== Valider et transfer de piece
    def open_liste_valide(self):
        liste_conv = ValidationPieces(self.dbfolder)
        liste_conv.exec_()

    def open_conver(self):
        open_ = DialogueConversion(self.dbfolder)
        open_.exec()

    # ================== Supprimer ===========================#
    def delete_fact_vent(self):
        """
        Supprime une ou plusieurs factures sélectionnées dans la QTableView.
        """
        con = self.cal.connect_to_db(self.dbfolder)
        if con is None:
            return
        cur = con.cursor()

        indexes = self.table.selectedIndexes()
        if not indexes:
            QMessageBox.warning(self, "Suppression", "Aucun élément sélectionné. Veuillez sélectionner une ou plusieurs lignes!")
            con.close()
            return
        rows = {index.row() for index in indexes}
        ids_to_delete = []
        try:
            model = self.table.model()
            if model is None:
                con.close()
                return

            for row in rows:
                id_index = model.index(row, self.COL_FACTURE)
                type_fact_index = model.index(row, self.COL_PIECE)

                facture_id = model.data(id_index)
                facture_type = model.data(type_fact_index)

                ids_to_delete.append({'id': facture_id, 'type': facture_type})

        except Exception as e:
            log.error(f"Une erreur est survenue lors de la récupération des données de sélection : {str(e)}", exc_info=True)
            QMessageBox.information(self, "Erreur", f"Une erreur est survenue lors de la récupération des données de sélection : {str(e)}")
            con.close()
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("SUPPRESSION")
        msg.setText("Êtes-vous sûr de vouloir supprimer les données de ces factures?")
        btn_yes = msg.addButton("Oui", QMessageBox.ButtonRole.YesRole)
        btn_no = msg.addButton("Non", QMessageBox.ButtonRole.NoRole)
        msg.exec_()

        try:
            if msg.clickedButton() == btn_yes:
                for item in ids_to_delete:
                    facture_id = item['id']
                    facture_type = item['type']
                    sql1 = "DELETE FROM vent WHERE facture = ?" if facture_type in ["Facture", "Ticket"] else "DELETE FROM liste WHERE facture = ?"
                    cur.execute(sql1, (facture_id,))
                    cur.execute("DELETE FROM infov WHERE factu=?", (facture_id,))
                con.commit()
                QMessageBox.information(self, "Succès", "Les factures ont été supprimées avec succès.")
            else:
                con.rollback()
                QMessageBox.information(self, "Annulation", "La suppression a été annulée.")
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)} dans delete_fact_vent", exc_info=True)
            QMessageBox.information(self, "Erreur", f"{e} dans delete_fact_vent")
            con.rollback()
        finally:
            con.close()
            self.refresh()

    # utilitaire pour obtenir la valeur de la cellule sélectionnée
    def _selected_row_value(self, col_index):
        model = self.table.model()
        index = self.table.currentIndex()
        if model is None or not index.isValid():
            return None
        row = index.row()
        idx = model.index(row, col_index)
        if not idx.isValid():
            return None
        return model.data(idx)

    # ============= Paiement ==================
    def credivente(self):
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            return
        try:
            invoice_id = self._selected_row_value(self.COL_FACTURE)
            if invoice_id is None:
                QMessageBox.warning(self, "Paiement", "Aucun élément sélectionné. Veillez sélectionner une ligne!")
                return

            cur = conn.cursor()
            sql = 'SELECT * FROM infov WHERE factu=?'
            cur.execute(sql, (invoice_id,))
            res = cur.fetchone()
            if not res:
                QMessageBox.warning(self, "Paiement", "Facture introuvable en base.")
                return

            self.type = res[9] if len(res) > 9 else None
            if self.type == "Facture":
                if res[7] != "En cours":
                    if res[7] == "Payé":
                        QMessageBox.information(self, "PAIEMENT", f'La facture <span style ="color:blue;"> {invoice_id}</span> est déjà entièrement payée.')
                        return
                    self.win44 = QDialog()
                    self.vdi = Ui_Ui_payereste()
                    self.vdi.setupUi(self.win44)
                    self.win44.show()
                    self.date = QDate.currentDate()
                    self.vdi.dateEdit.setDate(self.date)
                    self.load_compte()
                    self.vdi.comboBox.activated.connect(lambda: self.type_paiement())
                    self.vdi.pushButton.clicked.connect(lambda: self.handle_unpaid_invoice_payment())
                    self.vdi.reglELeResteSpinBox.valueChanged.connect(lambda: self.mise_statut())
                    try:
                        if res:
                            cur2 = conn.cursor()
                            cur2.execute('SELECT nom FROM client where id=?', (res[1],))
                            clit_row = cur2.fetchone()
                            clit = clit_row[0] if clit_row else None
                            if clit:
                                self.vdi.label_9.setText(str(clit))
                            else:
                                self.vdi.label_9.setText("client")
                            self.vdi.numeroFactureLineEdit.setText(str(res[0]))
                            self.vdi.montantTotalLineEdit.setText(str(res[2]))
                            self.vdi.lineEdit.setText(str(res[3]))
                            self.vdi.montantPayLineEdit.setText(str(res[4]))
                            self.vdi.montantRestantLineEdit.setText(str(res[5]))
                            self.vdi.label_8.setText(str(res[6]))
                            self.vdi.dateLineEdit.setText(str(res[8]))
                            if res[7] == "Impayé":
                                self.vdi.label_4.setText(str(res[7]))
                                self.vdi.label_4.setStyleSheet("background-color:red;color:white;")
                            elif res[7] == "Avance":
                                self.vdi.label_4.setText(str(res[7]))
                                self.vdi.label_4.setStyleSheet("background-color:blue;color:white;")
                            elif res[7] == "Payé":
                                self.vdi.label_4.setText(str(res[7]))
                                self.vdi.label_4.setStyleSheet("background-color:blue;color:white;")
                            else:
                                self.vdi.label_4.setStyleSheet("background-color:red;color:white;")
                                self.vdi.label_4.setText(str("Impayé"))
                            self.user = res[13] if len(res) > 13 else None
                            log.debug(f"Utilisateur trouvé pour la facture: {self.user}")
                    except Exception as e:
                        log.error(f"Une erreur est survenue: {str(e)} dans credivente", exc_info=True)
                    # NOTE: on ferme la connexion dans finally si nécessaire
                else:
                    QMessageBox.warning(self, "Action refusée", "Vous ne pouvez pas payer une facture en cours. Veiller Valider la facture")
                    return
            else:
                QMessageBox.information(self, "PAIEMENT", f'Paiement impossible pour <span style ="color:blue;"> {self.type}</span>. Veillez transformer en facture définitive !')
        except Exception as e:
            log.error(f"Erreur credivente: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    def load_compte(self):
        try:
            conn = self.cal.connect_to_db(self.dbfolder)
            if conn is None:
                return
            cur = conn.cursor()
            sql = "SELECT numCompte,inti FROM compte WHERE classe ='5'"
            cur.execute(sql)
            inf = cur.fetchall()
            self.vdi.comboBox_2.clear()
            for item in inf:
                self.vdi.comboBox_2.addItem(f"{item[0]} {item[1]}", userData=item[0])
        except Exception as e:
            log.warning(f"Erreur &1 :{str(e)} dans load_compte", exc_info=True)
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def mise_statut(self):
        try:
            payle = float(self.vdi.reglELeResteSpinBox.value())
            reste = float(self.vdi.montantRestantLineEdit.text())
            self.vdi.label_5.setText(str((reste - payle)))
            mnt = float(self.vdi.lineEdit.text())
            if (reste - payle) == 0.0 or payle > mnt:
                self.vdi.label_4.setText("Payé")
                self.vdi.label_4.setStyleSheet("background-color:green;color:white;")
            elif payle == 0.0:
                self.vdi.label_4.setText("Impayé")
            elif (reste - payle) < 0:
                self.vdi.label_4.setText("Payé")
                self.vdi.label_4.setStyleSheet("background-color:green;color:white;")
            else:
                self.vdi.label_4.setText("Avance")
                self.vdi.label_4.setStyleSheet("background-color:blue;color:white;")
        except Exception as e:
            log.error(f"Erreur mise_statut: {e}", exc_info=True)

    def type_paiement(self):
        moyen_paiem = self.vdi.comboBox.currentText()
        moyen = self.cal.code_paiement(moyen_paiem)
        facture = self.vdi.numeroFactureLineEdit.text()
        moyen_ = f"{moyen}-{facture}"
        self.vdi.label.setText(moyen_)

    def handle_unpaid_invoice_payment(self):
        """
        Traite le paiement d'une facture de vente non réglée et met à jour
        la base de données et les écritures comptables.
        """
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            QMessageBox.critical(self.win44, "Erreur de connexion", "Impossible de se connecter à la base de données.")
            return

        cur = conn.cursor()
        try:
            val = QDateTime.currentDateTime().toString("yyyy-MM-dd")
            invoice_number = self.vdi.numeroFactureLineEdit.text()
            payment_amount = float(self.vdi.reglELeResteSpinBox.value())

            # On récupère le TTC depuis lineEdit (vérifier que c'est le TTC)
            try:
                total_ttc = float(self.vdi.lineEdit.text())
            except Exception:
                QMessageBox.critical(self.win44, "Erreur", "Montant total invalide.")
                return

            payment_date_str = self.vdi.dateLineEdit.text().strip()
            numero_compte = self.vdi.comboBox_2.currentData()
            journal_text = self.vdi.comboBox_2.currentText() or ""
            # récupération prudente du texte de journal
            if " " in journal_text:
                journal = journal_text.split(' ', 1)[1]
            else:
                journal = journal_text
            ref = self.vdi.label.text()

            # Convertir la date du string en objet datetime (plusieurs formats possibles)
            payment_date = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    payment_date = datetime.datetime.strptime(payment_date_str, fmt)
                    break
                except Exception:
                    payment_date = None
            if payment_date is None:
                payment_date = datetime.datetime.now()
                log.warning(f"Format de date non reconnu: '{payment_date_str}', fallback sur now()")

            if not ref:
                QMessageBox.information(self.win44, "PAIEMENT", "Veuillez choisir un moyen de paiement et choisir la destination")
                return

            # Confirmation utilisateur
            msg = QMessageBox(self.win44)
            msg.setWindowTitle("MODIFICATION")
            msg.setText(f"Confirmez-vous le paiement de {payment_amount:,.2f} pour la facture {invoice_number}?")
            btn_yes = msg.addButton("Oui", QMessageBox.ButtonRole.YesRole)
            btn_no = msg.addButton("Non", QMessageBox.ButtonRole.NoRole)
            msg.exec_()

            if msg.clickedButton() == btn_yes:
                

                remaining_balance = total_ttc - payment_amount
                new_status = 'Payé' if remaining_balance <= 0.01 else 'Avance'

                cmd = '''
                    UPDATE infov
                    SET payer = payer + ?, monn = monn - ?, statut = ?, compta = ?
                    WHERE factu = ?
                '''
                data = (payment_amount, payment_amount, new_status, 'ENREGISTRE-COMPTA', invoice_number)
                cur.execute(cmd, data)
                # insérer trésorerie via l'objet cal
                try:
                    self.cal.insert_tresorerie(cur, val, "Reglement " + invoice_number, payment_amount, "ENTREE", numero_compte, self.user)
                except Exception as e:
                    log.warning(f"Impossible d'insérer en trésorerie: {e}", exc_info=True)

                conn.commit()
                QMessageBox.information(self.win44, "Paiement", "Paiement enregistré avec succès.")
            else:
                conn.rollback()
                QMessageBox.information(self.win44, "Paiement", "Paiement annulé.")

            self.win44.close()
        except sq.Error as e:
            conn.rollback()
            log.error(f"Erreur de base de données: {e}", exc_info=True)
            QMessageBox.critical(self.win44, "Erreur de BDD", f"Une erreur de base de données est survenue: {e}")
        except ValueError as e:
            conn.rollback()
            log.error(f"Erreur de conversion de valeur: {e}", exc_info=True)
            QMessageBox.critical(self.win44, "Erreur de donnée", f"Erreur lors de la lecture des données de l'interface: {e}")
        except Exception as e:
            conn.rollback()
            log.error(f"Une erreur inattendue est survenue: {e}", exc_info=True)
            QMessageBox.critical(self.win44, "Erreur", f"Une erreur inattendue est survenue: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
            self.refresh()

    # ==================== Avoir ou détails =================
    def details_(self):
        try:
            index = self.table.currentIndex().row()
            if index >= 0:
                affi = self.aff_detail()
                if not affi:
                    return
                data_frame, va = affi
                self.wind_detail = Details(self.dbfolder, data_frame, va)
                self.wind_detail.show()
            else:
                QMessageBox.warning(self, "Détails", "Veiller sélectionner la ligne!")
        except Exception as e:
            log.warning(f"Erreur :{str(e)} dans details_")

    def aff_detail(self):
        index = self.table.currentIndex().row()
        if index < 0:
            QMessageBox.warning(self, "Détails", "Veiller sélectionner la ligne!")
            return None
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            return None
        try:
            va = self._selected_row_value(self.COL_FACTURE)
            if va is None:
                log.error("No invoice id in aff_detail()")
                return None
            type_factu = self._selected_row_value(self.COL_PIECE)
            query = "SELECT facture,code,libelle, quantite,prix,montant FROM "
            if type_factu in ("Ticket", "Facture"):
                query += "vent where facture = ?"
            else:
                query += "liste where facture = ?"
            df = pd.read_sql_query(query, conn, params=[va])
            if df.empty:
                return None
            return df, va
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)} dans aff_detail", exc_info=True)
            QMessageBox.information(self, "erreur", f"{str(e)} dans aff_detail")
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # ===================== Impression =======================#
    def liste_article(self):
        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            log.error("Database connection failed in liste_article()")
            return []
        try:
            cur = conn.cursor()
            index = self.table.currentIndex()
            model = self.table.model()
            if model is None or not index.isValid():
                log.error("No model or invalid index in liste_article()")
                return []
            nindex = model.index(index.row(), self.COL_FACTURE)
            va = model.data(nindex)
            type_fact_index = model.index(index.row(), self.COL_PIECE)
            type_fact = model.data(type_fact_index)
            sql = "SELECT libelle, quantite,prix,montant FROM "
            if type_fact == "Facture":
                sql += "vent where facture =?"
                cur.execute(sql, (va,))
            else:
                sql += "liste where facture =?"
                cur.execute(sql, (va,))
            res = cur.fetchall()
            Data = []
            for item in res:
                if item not in Data:
                    Data.append(item)
            return Data
        except Exception as e:
            log.error(f"Erreur liste_article: {e}", exc_info=True)
            return []
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def Info(self):
        try:
            var_dic_vente = {}
            self.tva = 0.0
            self.date = "_"
            self.facto = "_"
            self.montant_verse = 0.0
            self.reste = 0.0
            self.nom_clt = "Client ordinaire"
            self.contact1 = "_"
            self.adresse1 = "_"
            self.type_fact = ""
            self.ville = "_"
            conn = self.cal.connect_to_db(self.dbfolder)
            if conn is None:
                return
            cur = conn.cursor()
            index = self.table.currentIndex()
            nindex = self.table.model()
            if nindex is None or not index.isValid():
                return
            va = self._selected_row_value(self.COL_FACTURE)
            if va is None:
                return
            pr_v = 'SELECT * from infov where factu=?'
            cur.execute(pr_v, [va])
            cv = cur.fetchone()
            if cv:
                # protections d'index
                self.tva = float(cv[6]) if cv[6] is not None else 0.0
                self.date = cv[8]
                self.facto = cv[0]
                self.montant_verse = cv[4]
                self.reste = cv[5]
                self.type_fact = cv[9]
                self.remarque = cv[12] if len(cv) > 12 and cv[12] else ""

            info = 'SELECT nom,cont,adr,ville from client where id=?'
            cur.execute(info, [cv[1] if cv else None])
            info_clt = cur.fetchone()
            if info_clt:
                self.nom_clt = info_clt[0]
                self.contact1 = info_clt[1]
                self.adresse1 = info_clt[2]
                self.ville = info_clt[3]

            var_dic_vente = {
                "Adrresse": self.adresse1,
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
            return var_dic_vente
        except Exception as e:
            log.error(f"Une erreur est survenue: {str(e)} dans Info", exc_info=True)
            QMessageBox.warning(self, "Erreour", f"{e} dans Info")
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def imprimerList_1(self):
        index = self.table.currentIndex().row()
        if index >= 0:
            try:
                temp_file_path = QDir.tempPath() + "/temp_document.html"
                try:
                    html = self.facture_generate()
                    if html is None:
                        return
                    with open(temp_file_path, "w", encoding="utf-8") as f:
                        f.write(html)
                    webbrowser.open(f"file:///{temp_file_path}")
                except Exception as e:
                    log.warning(f"Erreur lors de l'ouverture du fichier dans le navigateur : {e}", exc_info=True)
            except Exception as e:
                log.warning(f"Erreur :{str(e)}", exc_info=True)
        else:
            QMessageBox.warning(self, "Impression", "Veuillez selectionner la ligne à imprimer")

    

    def facture_generate(self):
        try:
            donne = self.liste_article()
            vente = self.Info()
            if vente is None:
                return None
            infoEntrp = self.cal.print_info(self.dbfolder)
            if infoEntrp is None:
                return None

            entr = infoEntrp.get('nom')
            T1 = infoEntrp.get('T1')
            T2 = infoEntrp.get('T2')
            info = infoEntrp.get('info')
            adre = infoEntrp.get('adresse')
            ville = infoEntrp.get('ville')
            respo = infoEntrp.get('resp')
            ifu = infoEntrp.get('ifu')
            autre = infoEntrp.get('autre')
            self.remarque = infoEntrp.get('remarque', '')
            date = datetime.datetime.now().strftime("%d/%m/%Y")
            self.type_fact = vente['type_facture']
            if self.type_fact == "Commande":
                self.msg = str('Bon de commande')
            elif self.type_fact == "Livraison":
                self.msg = str("Bon de livraison")
            elif self.type_fact == "Dévis":
                self.msg = str("Devis")
            else:
                self.msg = str("Facture")

            try:
                chemin = "logo"
                self.defaulImgSrc = os.listdir(chemin)[0]
                self.file_chemin = os.path.join(chemin, self.defaulImgSrc)
            except Exception:
                self.file_chemin = None

            html = self.Model.facture_(Entr=entr, T1=T1, T2=T2, info=info, ville=ville, adresse=adre, responsabable=respo, 
                                       list_article=donne, vente=vente, msg=self.msg, 
                                       ifu=ifu, autre=autre, chemin=self.file_chemin, 
                                       date=date,remarque=self.remarque)
            return html
        except Exception as e:
            log.error(f"Erreur facture_generate: {e}", exc_info=True)
            QMessageBox.warning(self, "Erreur", f"{e}")
            return None
    
    def imprimer_liste_pieces(self):
        """
        Génère un fichier HTML contenant la liste des pièces et l'ouvre dans le navigateur.
        L'utilisateur peut ensuite imprimer via le navigateur.
        """
        try:
            infoEntrp = self.cal.print_info(self.dbfolder)
            if infoEntrp is None:
                return None

            entr = infoEntrp.get('nom')
            T1 = infoEntrp.get('T1')
            T2 = infoEntrp.get('T2')
            # Construction du tableau HTML
            html = "<html><head>"
            html += "<meta charset='UTF-8'>"
            html += "<style>"
            html += "table { border-collapse: collapse; width: 100%; font-size: 13px; }"
            html += "th, td { border: 1px solid #000; padding: 4px; text-align: center; }"
            html += "th { background: #eee; }"
            html += "</style></head><body>"
            html += "<h2>Liste des pièces</h2>"
            html += "<table><thead><tr>"

            # En-têtes
            for col in self.cols:
                html += f"<th>{col}</th>"
            html += "</tr></thead><tbody>"

            # Données
            for row in self.full_rows:
                html += "<tr>"
                for val in row:
                    html += f"<td>{val}</td>"
                html += "</tr>"

            html += "</tbody></table></body></html>"

            # Emplacement temporaire
            temp_file_path = QDir.tempPath() + "/liste_des_pieces.html"

            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(html)

            # Ouvrir dans le navigateur
            webbrowser.open(f"file:///{temp_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'impression : {e}")

  
    def creer_avoir_depuis_facture(self):
        facture = self._selected_row_value(self.COL_FACTURE)
        print(f"Facture sélectionnée pour avoir : {facture}")
        if facture is None:
            QMessageBox.warning(self, "Avoir", "Sélectionnez une facture valide")
            return
        box = QMessageBox(self)
        box.setWindowTitle("Créer un avoir")
        box.setText(f"Créer un avoir pour la facture {facture} ?")

        btn_yes = box.addButton("Oui", QMessageBox.ButtonRole.AcceptRole)
        btn_no = box.addButton("Non", QMessageBox.ButtonRole.RejectRole)

        box.exec()
        if box.clickedButton() != btn_yes:
            return
        # Génération numéro AVOIR
        num_avoir = self.numeroteur.generer("AV")

        conn = self.cal.connect_to_db(self.dbfolder)
        if conn is None:
            QMessageBox.critical(self, "Erreur BD", "Impossible de se connecter à la base de données.")
            return
        cur = conn.cursor()

        # Récupérer facture originale
        cur.execute("SELECT * FROM infov WHERE factu=?", (facture,))
        row = cur.fetchone()
        if not row:
            QMessageBox.warning(self, "Erreur", "Facture introuvable")
            return

        # Insertion de l'avoir (montants négatifs)
        cur.execute("""
            INSERT INTO infov (
                factu, client, montant, mnt_ttc, payer, monn,
                datee, statut, type_fact, remarque, utilisateur, origine
            )
            VALUES (?, ?, ?, ?, 0.0, 0.0, ?,
                    'AVOIR', 'Avoir', ?, ?, ?)
        """, (
            num_avoir,
            row[2],
            -abs(row[3]),
            -abs(row[4]),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"Avoir sur facture {facture}",
            self.user,
            facture
        ))

        conn.commit()

        QMessageBox.information(
            self, "Avoir créé",
            f"Avoir {num_avoir} créé à partir de {facture}"
        )