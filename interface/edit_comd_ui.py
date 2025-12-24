# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_comd.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)


class Ui_dialog_edi(object):
    def setupUi(self, dialog_edi):
        if not dialog_edi.objectName():
            dialog_edi.setObjectName(u"dialog_edi")
        dialog_edi.resize(590, 360)
        dialog_edi.setMaximumSize(QSize(590, 360))
        font = QFont()
        font.setBold(True)
        font.setItalic(False)
        dialog_edi.setFont(font)
        dialog_edi.setAcceptDrops(True)
        icon = QIcon()
        icon.addFile(u":/icon/chariot-de-chariot.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        dialog_edi.setWindowIcon(icon)
        dialog_edi.setStyleSheet(u" QLabel {\n"
"        color: #2c3e50;\n"
"        font-size: 13px;\n"
"        font-weight: bold;\n"
"    }\n"
"\n"
"    /* QLineEdit */\n"
"    QLineEdit {\n"
"        border: 1px solid #ccc;\n"
"        border-radius: 4px;\n"
"        padding: 5px;\n"
"        font-size: 13px;\n"
"        background-color: #ffffff;\n"
"        selection-background-color: #a8dadc;\n"
"    }\n"
"\n"
"    QLineEdit:focus {\n"
"        border: 1px solid #0077b6;\n"
"        background-color: #f1faff;\n"
"    }\n"
"\n"
"    /* QPushButton */\n"
"    QPushButton {\n"
"        background-color: #7f85b6;\n"
"        color: white;\n"
"        padding: 6px 12px;\n"
"        border-radius: 5px;\n"
"        font-size: 13px;\n"
"    }\n"
"\n"
"    QPushButton:hover {\n"
"        background-color: #0096c7;\n"
"    }\n"
"\n"
"    QPushButton:pressed {\n"
"        background-color: #023e8a;\n"
"    }\n"
"")
        dialog_edi.setSizeGripEnabled(True)
        dialog_edi.setModal(True)
        self.verticalLayout = QVBoxLayout(dialog_edi)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(dialog_edi)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 30))
        self.frame.setMaximumSize(QSize(16777215, 50))
        self.frame.setStyleSheet(u"")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.frame.setLineWidth(2)
        self.frame.setMidLineWidth(2)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setFamilies([u"Verdana"])
        font1.setPointSize(15)
        font1.setBold(False)
        font1.setItalic(False)
        self.label.setFont(font1)
        self.label.setStyleSheet(u"font: 15pt \"Verdana\";")
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.label)


        self.verticalLayout.addWidget(self.frame, 0, Qt.AlignTop)

        self.frame_2 = QFrame(dialog_edi)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setStyleSheet(u"")
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Sunken)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.codeLineEdit = QLineEdit(self.frame_2)
        self.codeLineEdit.setObjectName(u"codeLineEdit")
        self.codeLineEdit.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.codeLineEdit.sizePolicy().hasHeightForWidth())
        self.codeLineEdit.setSizePolicy(sizePolicy1)
        self.codeLineEdit.setMinimumSize(QSize(0, 35))
        self.codeLineEdit.setMaximumSize(QSize(16777215, 35))
        font2 = QFont()
        font2.setFamilies([u"Verdana"])
        font2.setPointSize(12)
        self.codeLineEdit.setFont(font2)
        self.codeLineEdit.setStyleSheet(u"font: 12pt \"Verdana\";")
        self.codeLineEdit.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.codeLineEdit, 0, 2, 1, 1)

        self.produitLineEdit = QLineEdit(self.frame_2)
        self.produitLineEdit.setObjectName(u"produitLineEdit")
        self.produitLineEdit.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.produitLineEdit.sizePolicy().hasHeightForWidth())
        self.produitLineEdit.setSizePolicy(sizePolicy1)
        self.produitLineEdit.setMinimumSize(QSize(0, 35))
        self.produitLineEdit.setMaximumSize(QSize(16777215, 35))
        font3 = QFont()
        font3.setFamilies([u"Verdana"])
        font3.setPointSize(12)
        font3.setBold(False)
        font3.setItalic(False)
        self.produitLineEdit.setFont(font3)
        self.produitLineEdit.setStyleSheet(u"font: 12pt \"Verdana\";")
        self.produitLineEdit.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.produitLineEdit, 1, 2, 1, 1)

        self.prixLineEdit = QLineEdit(self.frame_2)
        self.prixLineEdit.setObjectName(u"prixLineEdit")
        self.prixLineEdit.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.prixLineEdit.sizePolicy().hasHeightForWidth())
        self.prixLineEdit.setSizePolicy(sizePolicy1)
        self.prixLineEdit.setMinimumSize(QSize(0, 35))
        self.prixLineEdit.setMaximumSize(QSize(16777215, 35))
        self.prixLineEdit.setFont(font3)
        self.prixLineEdit.setFocusPolicy(Qt.ClickFocus)
        self.prixLineEdit.setStyleSheet(u"font: 12pt \"Verdana\";")
        self.prixLineEdit.setMaxLength(32767)
        self.prixLineEdit.setAlignment(Qt.AlignCenter)
        self.prixLineEdit.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.prixLineEdit, 2, 2, 1, 1)

        self.quantitLineEdit = QDoubleSpinBox(self.frame_2)
        self.quantitLineEdit.setObjectName(u"quantitLineEdit")
        sizePolicy1.setHeightForWidth(self.quantitLineEdit.sizePolicy().hasHeightForWidth())
        self.quantitLineEdit.setSizePolicy(sizePolicy1)
        self.quantitLineEdit.setMinimumSize(QSize(0, 35))
        self.quantitLineEdit.setMaximumSize(QSize(16777215, 35))
        font4 = QFont()
        font4.setFamilies([u"Consolas"])
        font4.setPointSize(12)
        self.quantitLineEdit.setFont(font4)
        self.quantitLineEdit.setStyleSheet(u"")
        self.quantitLineEdit.setAlignment(Qt.AlignCenter)
        self.quantitLineEdit.setMaximum(100000000000000005366162204393472.000000000000000)

        self.gridLayout.addWidget(self.quantitLineEdit, 3, 2, 1, 1)

        self.montantLineEdit = QLineEdit(self.frame_2)
        self.montantLineEdit.setObjectName(u"montantLineEdit")
        self.montantLineEdit.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.montantLineEdit.sizePolicy().hasHeightForWidth())
        self.montantLineEdit.setSizePolicy(sizePolicy1)
        self.montantLineEdit.setMinimumSize(QSize(0, 35))
        self.montantLineEdit.setMaximumSize(QSize(16777215, 35))
        self.montantLineEdit.setFont(font3)
        self.montantLineEdit.setFocusPolicy(Qt.NoFocus)
        self.montantLineEdit.setStyleSheet(u"font: 12pt \"Verdana\";")
        self.montantLineEdit.setAlignment(Qt.AlignCenter)
        self.montantLineEdit.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.montantLineEdit, 6, 2, 1, 1)

        self.label_2 = QLabel(self.frame_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"font: 12pt \"Verdana\";")

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"font: 12pt \"Verdana\";")

        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)

        self.label_4 = QLabel(self.frame_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"font: 12pt \"Verdana\";")

        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 1)

        self.label_5 = QLabel(self.frame_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"font: 12pt \"Verdana\";")

        self.gridLayout.addWidget(self.label_5, 3, 1, 1, 1)

        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setStyleSheet(u"font: 12pt \"Verdana\";")

        self.gridLayout.addWidget(self.label_6, 6, 1, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(dialog_edi)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 30))
        self.frame_3.setMaximumSize(QSize(16777215, 50))
        self.frame_3.setStyleSheet(u"")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.pushButton = QPushButton(self.frame_3)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)
        self.pushButton.setMinimumSize(QSize(150, 0))
        self.pushButton.setMaximumSize(QSize(150, 16777215))
        font5 = QFont()
        self.pushButton.setFont(font5)
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton.setFocusPolicy(Qt.NoFocus)
        self.pushButton.setStyleSheet(u"background-color: green;\n"
"color: rgb(255, 255, 255);\n"
"border:1px solid ;\n"
"border-radius:7px;")

        self.horizontalLayout_3.addWidget(self.pushButton, 0, Qt.AlignRight)


        self.verticalLayout.addWidget(self.frame_3)


        self.retranslateUi(dialog_edi)

        QMetaObject.connectSlotsByName(dialog_edi)
    # setupUi

    def retranslateUi(self, dialog_edi):
        dialog_edi.setWindowTitle(QCoreApplication.translate("dialog_edi", u"Edition de la quantiter", None))
        self.label.setText(QCoreApplication.translate("dialog_edi", u"Editer les quantit\u00e9s", None))
        self.prixLineEdit.setInputMask("")
        self.label_2.setText(QCoreApplication.translate("dialog_edi", u"Code article", None))
        self.label_3.setText(QCoreApplication.translate("dialog_edi", u"Produit", None))
        self.label_4.setText(QCoreApplication.translate("dialog_edi", u"Prix", None))
        self.label_5.setText(QCoreApplication.translate("dialog_edi", u"Quantit\u00e9", None))
        self.label_6.setText(QCoreApplication.translate("dialog_edi", u"Montant", None))
        self.pushButton.setText(QCoreApplication.translate("dialog_edi", u"Valider", None))
    # retranslateUi

