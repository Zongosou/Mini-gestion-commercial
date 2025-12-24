# Vous devrez utiliser un éditeur d'interface graphique (comme Qt Designer) 
# pour générer ce code, mais voici la logique de remplacement :

from PySide6.QtCore import (QCoreApplication, QSize, Qt, QMetaObject)
from PySide6.QtGui import QIcon, QFont, QCursor
from PySide6.QtWidgets import (QCheckBox, QPushButton, QSizePolicy,
                               QRadioButton, QVBoxLayout, QWidget)

class Ui_creer_piece_moderne(object):
    def setupUi(self, creer_piece):
        if not creer_piece.objectName():
            creer_piece.setObjectName(u"creer_piece")
        creer_piece.setWindowModality(Qt.ApplicationModal)
        creer_piece.resize(316, 300)
        creer_piece.setMaximumSize(QSize(350, 300))
        icon = QIcon()
        icon.addFile(u":/icon/ajouter.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        creer_piece.setWindowIcon(icon)
        
        # ⚠️ SUPPRIMER LE STYLESHEET PRÉCÉDENT
        # On va appliquer le style "moderne" globalement.
        
        self.verticalLayout_2 = QVBoxLayout(creer_piece)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 20, 20, 20) # Marges plus uniformes

        font = QFont()
        font.setPointSize(12) # Taille de police légèrement réduite
        font.setBold(False) 
        
        # ⭐️ Remplacement des QCheckBox par QRadioButton ⭐️
        
        self.radio_devis = QRadioButton(creer_piece)
        self.radio_devis.setObjectName(u"radio_devis")
        self.radio_devis.setFont(font)
        self.verticalLayout.addWidget(self.radio_devis)
        
        self.radio_commande = QRadioButton(creer_piece)
        self.radio_commande.setObjectName(u"radio_commande")
        self.radio_commande.setFont(font)
        self.verticalLayout.addWidget(self.radio_commande)
        
        self.radio_livraison = QRadioButton(creer_piece)
        self.radio_livraison.setObjectName(u"radio_livraison")
        self.radio_livraison.setFont(font)
        self.verticalLayout.addWidget(self.radio_livraison)
        
        self.radio_facture = QRadioButton(creer_piece)
        self.radio_facture.setObjectName(u"radio_facture")
        self.radio_facture.setFont(font)
        self.verticalLayout.addWidget(self.radio_facture)
        
        self.verticalLayout_2.addLayout(self.verticalLayout)

        # Bouton Valider
        self.pushButton = QPushButton(creer_piece)
        self.pushButton.setObjectName(u"PrimaryButton")
        self.pushButton.setMinimumSize(QSize(0, 40)) # Augmentation de la hauteur
        self.pushButton.setMaximumSize(QSize(16777215, 40))
        
        self.pushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton.setFocusPolicy(Qt.NoFocus)
        # ⚠️ L'icône et le style du bouton seront appliqués par le CSS global (PrimaryButton)
        
        self.verticalLayout_2.addWidget(self.pushButton)

        self.retranslateUi(creer_piece)
        QMetaObject.connectSlotsByName(creer_piece)
        
    def retranslateUi(self, creer_piece):
        creer_piece.setWindowTitle(QCoreApplication.translate("creer_piece", u"Choisir le type de pi\u00e8ce", None))
        self.radio_devis.setText(QCoreApplication.translate("creer_piece", u"Devis", None))
        self.radio_commande.setText(QCoreApplication.translate("creer_piece", u"Commande", None))
        self.radio_livraison.setText(QCoreApplication.translate("creer_piece", u"Bon de livraison", None))
        self.radio_facture.setText(QCoreApplication.translate("creer_piece", u"Facture", None))
        self.pushButton.setText(QCoreApplication.translate("creer_piece", u"Valider et Cr\u00e9er", None))