from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame, QDialog,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from  fonction.methode import cal

class GestHistStock(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique des achats")
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Catégorie", "Quantité", "Prix (€)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        self._load_data()
    def _load_data(self):
        # Simuler le chargement des données depuis une base de données
        data = [
            {"id": 1, "name": "Produit A", "category": "Catégorie 1", "qty": 50, "price": 10.0},
            {"id": 2, "name": "Produit B", "category": "Catégorie 2", "qty": 20, "price": 15.5},
            {"id": 3, "name": "Produit C", "category": "Catégorie 1", "qty": 0, "price": 7.25},
        ]
        
        self.table.setRowCount(len(data))
        self._populate_table(data)
    def _populate_table(self, data):
         for row, product in enumerate(data):
             id_item = QTableWidgetItem(str(product["id"]))
             name_item = QTableWidgetItem(product["name"])
             cat_item = QTableWidgetItem(product["category"])
             qty_item = QTableWidgetItem(str(product["qty"]))
             prix_item = QTableWidgetItem(f"{product['price']:.2f} €")