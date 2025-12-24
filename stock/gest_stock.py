from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame, QDialog,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from  fonction.methode import cal
from stock.add_product_dialog import AddProductDialog
from stock.edit_product_dialog import EditProductDialog
from stock.stock_db import DataManage
import os
from stock.add_piece import AchatModule
class SummaryCard(QFrame):
    def __init__(self, title: str, value: str, accent: str = "#2D7EF7", parent=None):
        super().__init__(parent)
        self.setObjectName("SummaryCard")
        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        value_label = QLabel(value)

        title_label.setObjectName("SummaryTitle")
        value_label.setObjectName("SummaryValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.setContentsMargins(16, 12, 16, 16)

        # Accent bar on left
        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setStyleSheet(f"background-color: {accent}; border-radius: 2px;")
        container = QHBoxLayout()
        container.addWidget(accent_bar)
        container.addWidget(self._wrap(layout))
        container.setContentsMargins(0, 0, 0, 0)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addLayout(container)

    def _wrap(self, inner_layout):
        wrapper = QWidget()
        wrapper.setLayout(inner_layout)
        return wrapper

class StockApp(QWidget):
    def __init__(self,  db_connection="",  titre="Gestion de Stock"):
        super().__init__()
        self.titre = titre
        self.db_connection = db_connection
        self.cal = cal()
        self.dataSource = DataManage(db_connection)
    # ---------------------------
    # UI Builders
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel(f"{self.titre}")
        title.setObjectName("PageTitle")

        btn_add = QPushButton("Ajouter produit")
        btn_add.setIcon(QIcon(':/icon/ajouter.png'))
        btn_add.setObjectName("PrimaryButton")
        btn_add.setToolTip("Ajouter un nouveau produit au stock")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.open_add_product_dialog)
       

        btn_edit = QPushButton("Modifier")
        btn_edit.setIcon(QIcon(':/icon/updated.png'))
        btn_edit.setObjectName("EditButton")
        btn_edit.setToolTip("Modifier le produit sélectionné")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.clicked.connect(self.open_edit_product_dialog)
       
        btn_delete = QPushButton("Supprimer")
        btn_delete.setIcon(QIcon(':/icon/delete.png'))
        btn_delete.setObjectName("DangerButton")
        btn_delete.setToolTip("Supprimer le produit sélectionné")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(lambda: QMessageBox.information(self, "Info", "Fonctionnalité à venir 😎"))

        btn_inventory = QPushButton("Inventaire")
        btn_inventory.setIcon(QIcon(':/icon/inventaire.png'))
        btn_inventory.setObjectName("InvButton")
        btn_inventory.setToolTip("Générer un inventaire de stock")
        btn_inventory.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_inventory.clicked.connect(lambda: QMessageBox.information(self, "Info", "Fonctionnalité à venir 😎"))

        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setIcon(QIcon(':/icon/refresh.png'))
        btn_refresh.setObjectName("IconButton")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self._refresh)
        btn_refresh.setToolTip("Rafraîchir les données")
        
        btn_add_fact = QPushButton("Ajouter Facture")
        btn_add_fact.setIcon(QIcon(':/icon/facture_achat.png'))
        btn_add_fact.setObjectName("PrimaryButton")
        btn_add_fact.setToolTip("Ajouter une nouvelle facture d'achat")
        btn_add_fact.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_fact.clicked.connect(self.add_facture_achat)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_add)
        header.addWidget(btn_edit)
        header.addWidget(btn_inventory)
        header.addWidget(btn_delete)
        header.addWidget(btn_refresh)
        header.addWidget(btn_add_fact)
        layout.addLayout(header)

        # Summary cards
        cards_row = QHBoxLayout()
        self.card_total = SummaryCard("Nombre total de produits", "0", accent="#2D7EF7")
        self.card_alerts = SummaryCard("Alertes stock faible", "0", accent="#F59E0B")
        self.card_value = SummaryCard("Valeur totale du stock", "0.0", accent="#10B981")

        cards_row.addWidget(self.card_total)
        cards_row.addWidget(self.card_alerts)
        cards_row.addWidget(self.card_value)

        layout.addLayout(cards_row)

        # Table
        table_container = QFrame()
        table_container.setObjectName("TableContainer")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Reference","Nom", "Catégorie", "Quantité", "Prix achat","Prix vente", "Statut"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.btn_hist_achat = QPushButton("Historique des achats")
        self.btn_hist_achat.setIcon(QIcon(':/icon/historique.png'))
        self.btn_hist_achat.setObjectName("IconButton")
        self.btn_hist_achat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hist_achat.setToolTip("Voir l'historique des achats")
        self.btn_hist_achat.clicked.connect(lambda: QMessageBox.information(self, "Info", "Fonctionnalité à venir 😎"))
        
        table_layout.addWidget(self.table)
        table_layout.addWidget(self.btn_hist_achat, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(table_container, 1)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(container)

        self._populate_table()
        self._update_summary_cards(self.dataSource.get_all_products())

    def add_facture_achat(self):
        dialog = AchatModule(self.db_connection)
        dialog.exec()

    # Data display
    # ---------------------------
    def _populate_table(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        data = self.dataSource.get_all_products()
        if data is False:
            QMessageBox.critical(self, "Erreur", "Impossible de récupérer les données depuis la base de données.")
            return
        for item in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
           
            ref = QTableWidgetItem(str(item["ref"]))
            nom_item = QTableWidgetItem(item["produit"])
            cat_item = QTableWidgetItem(item["categorie"])

            qty_item = QTableWidgetItem(str(item["qty"]))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            prix_item = QTableWidgetItem(self.cal.separateur_milieur(item["price"]))
            prix_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            prix_item_vent = QTableWidgetItem(self.cal.separateur_milieur(item["price_vent"]))
            prix_item_vent.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            statut_text = "OK" if item["qty"] >= item["alert_min"] else "Faible"
            statut_item = QTableWidgetItem(statut_text)

            # Color coding
            if statut_text == "Faible":
                statut_item.setForeground(Qt.GlobalColor.red)
            else:
                statut_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 0, ref)
            self.table.setItem(row, 1, nom_item)
            self.table.setItem(row, 2, cat_item)
            self.table.setItem(row, 3, qty_item)
            self.table.setItem(row, 4, prix_item)
            self.table.setItem(row, 5, prix_item_vent)
            self.table.setItem(row, 6, statut_item)

    def _update_summary_cards(self, data):
        total_products = len(data)
        low_stock_alerts = sum(1 for p in data if p["qty"] < p["alert_min"])
        total_value = sum(p["qty"] * p["price"] for p in data)

        # Update labels inside cards
        self.card_total.findChild(QLabel, "SummaryValue").setText(str(total_products))
        self.card_alerts.findChild(QLabel, "SummaryValue").setText(str(low_stock_alerts))
        self.card_value.findChild(QLabel, "SummaryValue").setText(self.cal.separateur_milieur(total_value))

    def _refresh(self):
        self._populate_table()
        self._update_summary_cards(self.dataSource.get_all_products())

    # ---------------------------
    # Event Handlers    
    def open_add_product_dialog(self):
        dialog = AddProductDialog(db=self.db_connection,parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh()
    
    def open_edit_product_dialog(self, product_id):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne avant de continuer 😎")
            return
        product_id = self.table.item(row, 0)
        if product_id is None:
            QMessageBox.warning(self, "Erreur", "ID de produit introuvable 😭")
            return
        product_id = str(product_id.text())
        dialog = EditProductDialog(self.db_connection,product_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh()