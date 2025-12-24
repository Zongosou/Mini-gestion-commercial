from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox
from fonction.methode import Numeroteur
from stock.stock_db import DataManage

class AddProductDialog(QDialog):
    def __init__(self, db="",parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un produit")
        self.setFixedSize(320, 300) 
        self.numeroteur = Numeroteur(db)
        self.dataManage = DataManage(db)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.refe = QLineEdit()
        self.numeroteur_pr = self.numeroteur.preview_prdo()
        self.refe.setEnabled(False)
        self.refe.setReadOnly(True)
        self.refe.setText(self.numeroteur_pr)
        self.refe.setStyleSheet("background:#222264;color:#FFFFFF")
        self.refe.setFixedSize(200, 30)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du produit")
        self.name_edit.setFixedSize(200, 30)
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Catégorie du produit")
        self.category_edit.setFixedSize(200, 30)

        self.qty_spin = QSpinBox()
        self.qty_spin.setSuffix(" Unités")
        self.qty_spin.setRange(0, 999999)
        self.qty_spin.setFixedSize(200, 25)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9999999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setFixedSize(200, 30)
        self.price_spin.setPrefix("Prix achat: ")

        self.price_vente_spin = QDoubleSpinBox()
        self.price_vente_spin.setRange(0, 9999999999.99)
        self.price_vente_spin.setDecimals(2)
        self.price_vente_spin.setFixedSize(200, 30)
        self.price_vente_spin.setPrefix("Prix de vente : ")
        self.alert_spin = QSpinBox()
        self.alert_spin.setSuffix(" Unités")
        self.alert_spin.setRange(1, 9999)
        self.alert_spin.setValue(0)
        self.alert_spin.setFixedSize(200, 30)

        form.addRow("Référence :", self.refe)
        form.addRow("Nom :", self.name_edit)
        form.addRow("Catégorie :", self.category_edit)
        form.addRow("Quantité initiale :", self.qty_spin)
        form.addRow("Prix achat :", self.price_spin)
        form.addRow("Prix de vente :", self.price_vente_spin)
        form.addRow("Seuil d’alerte :", self.alert_spin)
        layout.addLayout(form)
        btn_add = QPushButton("Ajouter")
        btn_add.setObjectName("PrimaryButton")
        btn_add.clicked.connect(self.save)
        layout.addWidget(btn_add)

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom du produit est obligatoire.")
            return

        self.dataManage.add_product(
            self.refe.text().strip(),
            name,
            self.category_edit.text(),
            self.qty_spin.value(),
            self.price_spin.value(),
            self.price_vente_spin.value(),
            self.alert_spin.value()
        )

        QMessageBox.information(self, "Succès", "Produit ajouté avec succès.")
        self.accept()
