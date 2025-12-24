import webbrowser
from PySide6.QtWidgets import (QWidget,QMainWindow, QVBoxLayout, QLabel, QTableWidget,QHeaderView, 
                               QTableWidgetItem,QHBoxLayout, QDateEdit, QComboBox,
                                 QPushButton, QFileDialog, QMessageBox, QTabWidget)
from PySide6.QtCore import QDate,QDir,Qt
from PySide6.QtGui import QIcon 
from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis
from PySide6.QtGui import QPainter
import sqlite3
from compta.ecriture import NewTresorerieOp
from fonction.methode import cal
from fonction.model import Model

class SuiviTresorerie(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.setWindowIcon(QIcon(':/icon/chariot-de-chariot.png'))
        self.setWindowTitle("Suivi de Trésorerie")
        self.resize(900, 520)
        self.Model = Model()
        self.cal = cal()
        self.charged = self.cal.charger_configuration_paie()
        charge_devise = self.cal.charger_tva_devise(self.db_path)
        # Configuration par défaut si non trouvée
        self.devise = charge_devise["devise"] if charge_devise else "CFA"
        self.tva = charge_devise["tva"] if charge_devise else "0.0"
        layout = QVBoxLayout(self)
        # --- Filtres ---
        filter_layout = QHBoxLayout()
        self.btn_ajout = QPushButton("Ajouter Opération")
        self.btn_ajout.setIcon(QIcon(":/icon/caisse-enregistreuse.png"))
        self.btn_ajout.setToolTip("Ajouter une nouvelle opération de trésorerie")
        self.btn_ajout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ajout.setObjectName("PrimaryButton")
        self.btn_ajout.clicked.connect(self.add_operation)
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # dernier mois par défaut
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QDate.currentDate())
        self.compte_combo = QComboBox()
        self.compte_combo.addItem("Tous les comptes", None)
        self.compte_combo.addItem("Caisse", "Caisse")
        self.compte_combo.addItem("Banque", "Banque")
        self.compte_combo.addItem("Compte Mobile", "Autre")  # tu peux enrichir dynamiquement
        self.btn_apply = QPushButton("Appliquer")
        self.btn_apply.setIcon(QIcon(":/icon/filtre.png"))
        self.btn_apply.setToolTip("Appliquer les filtres")
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setObjectName("PrimaryButton")
        self.btn_apply.clicked.connect(self.refresh)
        filter_layout.addWidget(self.btn_ajout)
        filter_layout.addWidget(QLabel("Du:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("Au:"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(QLabel("Compte:"))
        filter_layout.addWidget(self.compte_combo)
        filter_layout.addWidget(self.btn_apply)
        layout.addLayout(filter_layout)
        # --- Tableau ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Libellé", "Type", "Montant", "Compte", "Solde Cumulé"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        # --- Label total ---
        self.label_total = QLabel()
        self.label_total.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(self.label_total)
        export_layout = QHBoxLayout()
        
        self.btn_export_pdf = QPushButton("Imprimer")
        self.btn_export_pdf.setIcon(QIcon.fromTheme("printer"))
        self.btn_export_pdf.setToolTip("Imprimer le rapport de trésorerie")
        self.btn_export_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_pdf.setObjectName("PrimaryButton")

        refresh_button = QPushButton("Actualiser")
        refresh_button.setIcon(QIcon(":/icon/refresh.png"))
        refresh_button.setToolTip("Rafraîchir les données")
        refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_button.setObjectName("IconButton")
        refresh_button.clicked.connect(self.refresh)
        self.btn_export_pdf.clicked.connect(self.print_tresoreri)
        export_layout.addWidget(refresh_button)
        export_layout.addWidget(self.btn_export_pdf)
        layout.addLayout(export_layout)
        # Chargement initial
        self.refresh()

    def refresh(self):
        """Recharge le tableau en fonction des filtres"""
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        compte_filter = self.compte_combo.currentData()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        query = "SELECT date_operation, libelle, type, montant, compte FROM tresorerie WHERE date_operation BETWEEN ? AND ?"
        params = [date_from, date_to]
        if compte_filter:
            query += " AND compte = ?"
            params.append(compte_filter)
        query += " ORDER BY date_operation ASC, id ASC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        # Remplissage tableau + calcul des totaux
        self.table.setRowCount(0)
        solde = 0.0
        total_entrees = 0.0
        total_sorties = 0.0
        for row in rows:
            date, libelle, type_op, montant, compte = row
            montant = float(montant)
            if type_op == "ENTREE":
                solde += montant
                total_entrees += montant
            else:
                solde -= montant
                total_sorties += montant
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(date))
            self.table.setItem(r, 1, QTableWidgetItem(libelle))
            self.table.setItem(r, 2, QTableWidgetItem(type_op))
            self.table.setItem(r, 3, QTableWidgetItem(f"{self.cal.separateur_milieur(montant)} {self.devise}"))
            self.table.setItem(r, 4, QTableWidgetItem(compte))
            # solde_ = f"{solde:,.2f}".replace(","," ").replace(".",",")
            self.table.setItem(r, 5, QTableWidgetItem(f"{self.cal.separateur_milieur(solde)} {self.devise}"))
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # --- Mise à jour du résumé ---
        self.label_total.setText(
            f"✅ Total Entrées : {self.cal.separateur_milieur(total_entrees)} {self.devise} | ❌ Total Sorties : {self.cal.separateur_milieur(total_sorties)} {self.devise}| 💰 Solde Final : {self.cal.separateur_milieur(solde)} {self.devise}"
        )

    def export_excel(self):
        """Export des données en Excel"""
        path, _ = QFileDialog.getSaveFileName(self, "Exporter en Excel", "", "Fichier Excel (*.xlsx)")
        if not path:
            return

        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            if ws is None:
                ws = wb.create_sheet()
            ws.title = "Trésorerie"

            # En-têtes
            headers = ["Date", "Libellé", "Type", "Montant", "Compte", "Solde Cumulé"]
            ws.append(headers)

            # Données
            for row in range(self.table.rowCount()):
                values = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    values.append(item.text() if item else "")
                ws.append(values)

            # Totaux
            ws.append([])
            ws.append([self.label_total.text()])

            wb.save(path)
            QMessageBox.information(self, "Export Excel", f"Export réussi vers {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Export Excel", str(e))
 
    def ouvrir_html(self,html):
        temp_file_path = QDir.tempPath() + "/temp_document.html"
        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open(f"file:///{temp_file_path}")
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier dans le navigateur : {e}")
    
    def templa_(self):
        infoEntrp = self.cal.print_info(self.db_path)
        if infoEntrp is None:
            return
        entr, T1, T2 = infoEntrp['nom'], infoEntrp['T1'], infoEntrp['T2']
        info, ville, adre = infoEntrp['info'], infoEntrp['ville'], infoEntrp['adresse']
        ifu = infoEntrp['ifu']
        autre = infoEntrp['autre']
        html = self.Model.genere_model2(entr, T1, T2, info, ville, adre, self.table, msg="Rapport de Trésorerie", ifu=ifu, autre=autre)
        return html
    
    def print_tresoreri(self):
        html = self.templa_()
        if html is None:
            return
        self.ouvrir_html(html)
    def add_operation(self):
        self.op = NewTresorerieOp(self.db_path)
        self.op.exec()       

class RapportManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def _query(self, sql, params=()):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def ventes_mensuelles(self):
        return self._query("""
            SELECT strftime('%m', datee) as mois, SUM(montant)
            FROM infov
            WHERE type_fact='Facture'
            GROUP BY mois
            ORDER BY mois
        """)

    def ca_total(self):
        row = self._query("SELECT SUM(montant) FROM infov WHERE type_fact='Facture'")
        return row[0][0] if row and row[0][0] else 0

    def nb_factures(self):
        row = self._query("SELECT COUNT(*) FROM infov WHERE type_fact='Facture'")
        return row[0][0] if row else 0

    def panier_moyen(self):
        ca = self.ca_total()
        nb = self.nb_factures()
        return ca / nb if nb > 0 else 0

    def resume_tresorerie(self):
        return self._query("""
            SELECT compte, 
                   SUM(CASE WHEN type='ENTREE' THEN montant ELSE 0 END) as entree,
                   SUM(CASE WHEN type='SORTIE' THEN montant ELSE 0 END) as sortie
            FROM tresorerie
            GROUP BY compte
        """)

    def journal_comptable(self):
        return self._query("""
            SELECT date, journal, compte, type_operation,type_document 
            FROM ecritures_comptables
            ORDER BY date DESC
        """)

class RapportPro(QTabWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        # Onglets
        self.addTab(self._tab_statistiques(), "Statistiques")
        self.addTab(self._tab_tresorerie(), "Trésorerie")
        self.addTab(self._tab_journal(), "Journal")

    def _tab_statistiques(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Indicateurs clés
        ca_total = self.manager.ca_total()
        nb_factures = self.manager.nb_factures()
        panier = self.manager.panier_moyen()

        layout.addWidget(QLabel(f"CA Total : {ca_total:.2f}"))
        layout.addWidget(QLabel(f"Nombre de factures : {nb_factures}"))
        layout.addWidget(QLabel(f"Panier moyen : {panier:.2f}"))

        # Graphique ventes mensuelles
        data = self.manager.ventes_mensuelles()
        if data:
            mois = [m for m, _ in data]
            valeurs = [float(v) for _, v in data]

            barset = QBarSet("CA Mensuel")
            barset.append(valeurs)

            series = QBarSeries()
            series.append(barset)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Chiffre d'affaires mensuel")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

            axisX = QBarCategoryAxis()
            axisX.append(mois)
            chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axisX)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            layout.addWidget(chart_view)

        return tab

    def _tab_tresorerie(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        table = QTableWidget()
        resume = self.manager.resume_tresorerie()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Compte", "Entrées", "Sorties", "Solde"])
        table.setRowCount(len(resume))

        for row, (compte, entree, sortie) in enumerate(resume):
            solde = (entree or 0) - (sortie or 0)
            table.setItem(row, 0, QTableWidgetItem(str(compte)))
            table.setItem(row, 1, QTableWidgetItem(str(entree)))
            table.setItem(row, 2, QTableWidgetItem(str(sortie)))
            table.setItem(row, 3, QTableWidgetItem(str(solde)))

        layout.addWidget(table)
        return tab

    def _tab_journal(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        table = QTableWidget()
        journal = self.manager.journal_comptable()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Date", "Journal", "Compte", "Débit", "Crédit"])
        table.setRowCount(len(journal))

        for row, (date, journal, compte, debit, credit) in enumerate(journal):
            table.setItem(row, 0, QTableWidgetItem(str(date)))
            table.setItem(row, 1, QTableWidgetItem(str(journal)))
            table.setItem(row, 2, QTableWidgetItem(str(compte)))
            table.setItem(row, 3, QTableWidgetItem(str(debit)))
            table.setItem(row, 4, QTableWidgetItem(str(credit)))

        # Bouton export
        btn_export = QPushButton("Exporter en Excel/PDF")
        layout.addWidget(table)
        layout.addWidget(btn_export)

        return tab



class RapportWindow(QMainWindow):
    def __init__(self, db_path):
        super().__init__()
        self.setWindowTitle("Module Rapports & Analyses")
        self.resize(1000, 700)

        # Initialisation du manager (accès BD)
        self.manager = RapportManager(db_path)

        # Widget central
        central = QWidget()
        layout = QVBoxLayout(central)

        # Onglets de rapport (Stat, Trésorerie, Journal)
        self.rapport_tabs = RapportPro(self.manager)
        layout.addWidget(self.rapport_tabs)

        self.setCentralWidget(central)
