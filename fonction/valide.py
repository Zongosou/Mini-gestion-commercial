# auteur: zongo soumaïla
# Tel: +226 54267778 / 70925613
from interface.piece_ui import Ui_creer_piece_moderne
from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import Signal



class choixPiece(QDialog):
    pieceChoisie = Signal(str)
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_creer_piece_moderne()
        self.ui.setupUi(self)
        # self.mode = mode
        # self.current_user = current_user  # <<< utilisateur connecté passé depuis login
        
        self.type_piece =None
        
        self.ui.pushButton.clicked.connect(self.validateSelection)


    def validateSelection(self):
        selected_pieces = []
        if self.ui.radio_devis.isChecked():
            selected_pieces.append(self.ui.radio_devis.text())
            self.pieceChoisie.emit("DV")
        if self.ui.radio_commande.isChecked():
            selected_pieces.append(self.ui.radio_commande.text())
            self.pieceChoisie.emit("CM")
        if self.ui.radio_livraison.isChecked():
            selected_pieces.append(self.ui.radio_livraison.text())
            self.pieceChoisie.emit("BL")
        if self.ui.radio_facture.isChecked():
            selected_pieces.append(self.ui.radio_facture.text())
            self.pieceChoisie.emit("FAC")
        if not selected_pieces:
            QMessageBox.information(self, "Attention", "Veuillez sélectionner au moins une pièce.")
        else:
            self.close()
            for piece in selected_pieces:
                if piece in ["Facture", "Commande", "Devis", "Bon de livraison"]:
                    self.type_piece = piece
                    return self.type_piece
                else:
                    QMessageBox.warning(self, "Attention", "Type de pièce non reconnu.")
    