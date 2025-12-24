from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox, QLabel
from stock.stock_db import DataManage

class EditProductDialog(QDialog):
    def __init__(self, db="",product_id=str, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("Modifier un produit")
        self.setFixedSize(320, 300) 
        self.dataManage = DataManage(db)
        product = self.dataManage.get_product_by_id(product_id)
        if not product:
            QMessageBox.critical(self, "Erreur", "Produit introuvable.")
            self.close()
            return

        pid, name, category, qty, price, alert = product

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.ref = QLabel(str(pid))
        form.addRow("Référence :", self.ref)
        self.name_edit = QLineEdit(name)
        self.category_edit = QLineEdit(category if category else "")
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(0, 999999)
        self.qty_spin.setValue(qty)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9999999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(price)

        self.alert_spin = QSpinBox()
        self.alert_spin.setRange(1, 9999)
        self.alert_spin.setValue(alert)

        form.addRow("Référence :", self.ref)
        form.addRow("Nom :", self.name_edit)
        form.addRow("Catégorie :", self.category_edit)
        form.addRow("Quantité :", self.qty_spin)
        form.addRow("Prix :", self.price_spin)
        form.addRow("Seuil :", self.alert_spin)

        layout.addLayout(form)

        btn = QPushButton("Enregistrer")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

    def save(self):
        self.dataManage.update_product(
            self.product_id,
            self.name_edit.text(),
            self.category_edit.text(),
            self.qty_spin.value(),
            self.price_spin.value(),
            self.alert_spin.value()
        )

        QMessageBox.information(self, "Succès", "Produit modifié.")
        self.accept()
