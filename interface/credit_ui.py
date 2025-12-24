# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'credit.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDialog,
    QDoubleSpinBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)


class Ui_Ui_payereste(object):
    def setupUi(self, Ui_payereste):
        if not Ui_payereste.objectName():
            Ui_payereste.setObjectName(u"Ui_payereste")
        Ui_payereste.setWindowModality(Qt.ApplicationModal)
        Ui_payereste.resize(603, 562)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(False)
        Ui_payereste.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icon/credit.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Ui_payereste.setWindowIcon(icon)
        Ui_payereste.setStyleSheet(u" QLabel {\n"
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
"        background-color: #ffffff;\n"
"    \n"
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
"	font: 12pt \"Verdana\";\n"
"      \n"
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
        Ui_payereste.setSizeGripEnabled(True)
        Ui_payereste.setModal(True)
        self.verticalLayout = QVBoxLayout(Ui_payereste)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.groupBox = QGroupBox(Ui_payereste)
        self.groupBox.setObjectName(u"groupBox")
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        font1.setItalic(False)
        self.groupBox.setFont(font1)
        self.groupBox.setFlat(True)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lineEdit = QLabel(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setEnabled(False)
        self.lineEdit.setMinimumSize(QSize(0, 25))
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.lineEdit.setFont(font2)
        self.lineEdit.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.lineEdit.setFrameShape(QFrame.Box)
        self.lineEdit.setFrameShadow(QFrame.Plain)
        self.lineEdit.setLineWidth(1)
        self.lineEdit.setMidLineWidth(0)
        self.lineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.lineEdit, 5, 1, 1, 1)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(0, 25))
        self.label_9.setStyleSheet(u"font-size:10pt;background-color: rgb(255, 255, 255);")
        self.label_9.setFrameShape(QFrame.Box)

        self.gridLayout_2.addWidget(self.label_9, 3, 1, 1, 1)

        self.montantRestantLineEdit = QLabel(self.groupBox)
        self.montantRestantLineEdit.setObjectName(u"montantRestantLineEdit")
        self.montantRestantLineEdit.setEnabled(False)
        self.montantRestantLineEdit.setMinimumSize(QSize(0, 25))
        self.montantRestantLineEdit.setFont(font2)
        self.montantRestantLineEdit.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.montantRestantLineEdit.setFrameShape(QFrame.Box)
        self.montantRestantLineEdit.setFrameShadow(QFrame.Plain)
        self.montantRestantLineEdit.setLineWidth(1)
        self.montantRestantLineEdit.setMidLineWidth(0)
        self.montantRestantLineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.montantRestantLineEdit, 7, 1, 1, 1)

        self.montantRestantLabel = QLabel(self.groupBox)
        self.montantRestantLabel.setObjectName(u"montantRestantLabel")
        self.montantRestantLabel.setFont(font2)
        self.montantRestantLabel.setStyleSheet(u"font-size:10pt;")
        self.montantRestantLabel.setFrameShape(QFrame.NoFrame)
        self.montantRestantLabel.setFrameShadow(QFrame.Sunken)
        self.montantRestantLabel.setLineWidth(2)
        self.montantRestantLabel.setMidLineWidth(2)
        self.montantRestantLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.montantRestantLabel, 7, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setEnabled(False)
        self.label_4.setMinimumSize(QSize(0, 25))
        self.label_4.setFont(font2)
        self.label_4.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.label_4.setFrameShape(QFrame.Box)
        self.label_4.setFrameShadow(QFrame.Plain)
        self.label_4.setLineWidth(1)
        self.label_4.setMidLineWidth(0)
        self.label_4.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_4, 8, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font2)
        self.label_3.setStyleSheet(u"font-size:10pt;")
        self.label_3.setFrameShape(QFrame.NoFrame)
        self.label_3.setFrameShadow(QFrame.Sunken)
        self.label_3.setLineWidth(0)
        self.label_3.setMidLineWidth(0)
        self.label_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_3, 8, 0, 1, 1)

        self.montantPayLabel = QLabel(self.groupBox)
        self.montantPayLabel.setObjectName(u"montantPayLabel")
        self.montantPayLabel.setFont(font2)
        self.montantPayLabel.setStyleSheet(u"font-size:10pt;\n"
"")
        self.montantPayLabel.setFrameShape(QFrame.NoFrame)
        self.montantPayLabel.setFrameShadow(QFrame.Sunken)
        self.montantPayLabel.setLineWidth(2)
        self.montantPayLabel.setMidLineWidth(2)
        self.montantPayLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.montantPayLabel, 6, 0, 1, 1)

        self.dateLabel = QLabel(self.groupBox)
        self.dateLabel.setObjectName(u"dateLabel")
        self.dateLabel.setFont(font2)
        self.dateLabel.setStyleSheet(u"font-size:10pt;")
        self.dateLabel.setFrameShape(QFrame.NoFrame)
        self.dateLabel.setFrameShadow(QFrame.Sunken)
        self.dateLabel.setLineWidth(0)
        self.dateLabel.setMidLineWidth(0)
        self.dateLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.dateLabel, 2, 0, 1, 1)

        self.montantPayLineEdit = QLabel(self.groupBox)
        self.montantPayLineEdit.setObjectName(u"montantPayLineEdit")
        self.montantPayLineEdit.setEnabled(False)
        self.montantPayLineEdit.setMinimumSize(QSize(0, 25))
        self.montantPayLineEdit.setFont(font2)
        self.montantPayLineEdit.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.montantPayLineEdit.setFrameShape(QFrame.Box)
        self.montantPayLineEdit.setFrameShadow(QFrame.Plain)
        self.montantPayLineEdit.setLineWidth(1)
        self.montantPayLineEdit.setMidLineWidth(0)
        self.montantPayLineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.montantPayLineEdit, 6, 1, 1, 1)

        self.numeroFactureLineEdit = QLabel(self.groupBox)
        self.numeroFactureLineEdit.setObjectName(u"numeroFactureLineEdit")
        self.numeroFactureLineEdit.setEnabled(False)
        self.numeroFactureLineEdit.setMinimumSize(QSize(0, 25))
        self.numeroFactureLineEdit.setFont(font2)
        self.numeroFactureLineEdit.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.numeroFactureLineEdit.setFrameShape(QFrame.Box)
        self.numeroFactureLineEdit.setFrameShadow(QFrame.Plain)
        self.numeroFactureLineEdit.setLineWidth(1)
        self.numeroFactureLineEdit.setMidLineWidth(0)
        self.numeroFactureLineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.numeroFactureLineEdit, 0, 1, 1, 1)

        self.dateLineEdit = QLabel(self.groupBox)
        self.dateLineEdit.setObjectName(u"dateLineEdit")
        self.dateLineEdit.setEnabled(False)
        self.dateLineEdit.setMinimumSize(QSize(0, 25))
        self.dateLineEdit.setFont(font2)
        self.dateLineEdit.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.dateLineEdit.setFrameShape(QFrame.Box)
        self.dateLineEdit.setFrameShadow(QFrame.Plain)
        self.dateLineEdit.setLineWidth(1)
        self.dateLineEdit.setMidLineWidth(0)
        self.dateLineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.dateLineEdit, 2, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font2)
        self.label_2.setStyleSheet(u"font-size:10pt;")
        self.label_2.setFrameShape(QFrame.NoFrame)
        self.label_2.setFrameShadow(QFrame.Sunken)
        self.label_2.setLineWidth(2)
        self.label_2.setMidLineWidth(2)
        self.label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_2, 5, 0, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"font-size:10pt;")

        self.gridLayout_2.addWidget(self.label_7, 3, 0, 1, 1)

        self.numeroFactureLabel = QLabel(self.groupBox)
        self.numeroFactureLabel.setObjectName(u"numeroFactureLabel")
        self.numeroFactureLabel.setFont(font2)
        self.numeroFactureLabel.setStyleSheet(u"font-size:10pt;")
        self.numeroFactureLabel.setFrameShape(QFrame.NoFrame)
        self.numeroFactureLabel.setFrameShadow(QFrame.Sunken)
        self.numeroFactureLabel.setLineWidth(0)
        self.numeroFactureLabel.setMidLineWidth(0)
        self.numeroFactureLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.numeroFactureLabel, 0, 0, 1, 1)

        self.montantTotalLabel = QLabel(self.groupBox)
        self.montantTotalLabel.setObjectName(u"montantTotalLabel")
        self.montantTotalLabel.setFont(font2)
        self.montantTotalLabel.setStyleSheet(u"font-size:10pt;")
        self.montantTotalLabel.setFrameShape(QFrame.NoFrame)
        self.montantTotalLabel.setFrameShadow(QFrame.Sunken)
        self.montantTotalLabel.setLineWidth(2)
        self.montantTotalLabel.setMidLineWidth(2)
        self.montantTotalLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.montantTotalLabel, 4, 0, 1, 1)

        self.montantTotalLineEdit = QLabel(self.groupBox)
        self.montantTotalLineEdit.setObjectName(u"montantTotalLineEdit")
        self.montantTotalLineEdit.setEnabled(False)
        self.montantTotalLineEdit.setMinimumSize(QSize(0, 25))
        self.montantTotalLineEdit.setFont(font2)
        self.montantTotalLineEdit.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.montantTotalLineEdit.setFrameShape(QFrame.Box)
        self.montantTotalLineEdit.setFrameShadow(QFrame.Plain)
        self.montantTotalLineEdit.setLineWidth(1)
        self.montantTotalLineEdit.setMidLineWidth(0)
        self.montantTotalLineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.montantTotalLineEdit, 4, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_2)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(Ui_payereste)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setFont(font1)
        self.groupBox_2.setFlat(True)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"font-size:10pt;")

        self.gridLayout_3.addWidget(self.label_12, 3, 0, 1, 1)

        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setStyleSheet(u"font-size:10pt;")

        self.gridLayout_3.addWidget(self.label_11, 2, 0, 1, 1)

        self.reglELeResteLabel = QLabel(self.groupBox_2)
        self.reglELeResteLabel.setObjectName(u"reglELeResteLabel")
        self.reglELeResteLabel.setFont(font2)
        self.reglELeResteLabel.setStyleSheet(u"font-size:10pt;")
        self.reglELeResteLabel.setFrameShape(QFrame.NoFrame)
        self.reglELeResteLabel.setFrameShadow(QFrame.Sunken)
        self.reglELeResteLabel.setLineWidth(2)
        self.reglELeResteLabel.setMidLineWidth(2)
        self.reglELeResteLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.reglELeResteLabel, 0, 0, 1, 1)

        self.reglELeResteSpinBox = QDoubleSpinBox(self.groupBox_2)
        self.reglELeResteSpinBox.setObjectName(u"reglELeResteSpinBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reglELeResteSpinBox.sizePolicy().hasHeightForWidth())
        self.reglELeResteSpinBox.setSizePolicy(sizePolicy)
        self.reglELeResteSpinBox.setMinimumSize(QSize(0, 25))
        font3 = QFont()
        font3.setFamilies([u"Consolas"])
        font3.setPointSize(12)
        font3.setBold(False)
        self.reglELeResteSpinBox.setFont(font3)
        self.reglELeResteSpinBox.setAlignment(Qt.AlignCenter)
        self.reglELeResteSpinBox.setMaximum(999999999999.000000000000000)

        self.gridLayout_3.addWidget(self.reglELeResteSpinBox, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setStyleSheet(u"font-size:10pt;")

        self.gridLayout_3.addWidget(self.label_10, 1, 0, 1, 1)

        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setStyleSheet(u"font-size:10pt;")

        self.gridLayout_3.addWidget(self.label_13, 4, 0, 1, 1)

        self.comboBox = QComboBox(self.groupBox_2)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMinimumSize(QSize(0, 25))
        self.comboBox.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.comboBox, 1, 1, 1, 1)

        self.dateEdit = QDateEdit(self.groupBox_2)
        self.dateEdit.setObjectName(u"dateEdit")
        sizePolicy.setHeightForWidth(self.dateEdit.sizePolicy().hasHeightForWidth())
        self.dateEdit.setSizePolicy(sizePolicy)
        self.dateEdit.setMinimumSize(QSize(0, 25))
        font4 = QFont()
        font4.setPointSize(10)
        self.dateEdit.setFont(font4)

        self.gridLayout_3.addWidget(self.dateEdit, 2, 1, 1, 1)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 25))
        self.label.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.label.setFrameShape(QFrame.Box)

        self.gridLayout_3.addWidget(self.label, 3, 1, 1, 1)

        self.comboBox_2 = QComboBox(self.groupBox_2)
        self.comboBox_2.setObjectName(u"comboBox_2")
        sizePolicy.setHeightForWidth(self.comboBox_2.sizePolicy().hasHeightForWidth())
        self.comboBox_2.setSizePolicy(sizePolicy)
        self.comboBox_2.setMinimumSize(QSize(0, 25))
        self.comboBox_2.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.comboBox_2, 4, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_3)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setEnabled(False)
        self.label_8.setMinimumSize(QSize(0, 25))
        self.label_8.setFont(font2)
        self.label_8.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.label_8.setFrameShape(QFrame.Box)
        self.label_8.setFrameShadow(QFrame.Plain)
        self.label_8.setLineWidth(1)
        self.label_8.setMidLineWidth(0)
        self.label_8.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_3.addWidget(self.label_8)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.frame_3 = QFrame(Ui_payereste)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setStyleSheet(u"")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 5, 5, 5)
        self.label_5 = QLabel(self.frame_3)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setMinimumSize(QSize(0, 25))
        self.label_5.setMaximumSize(QSize(16777215, 25))
        self.label_5.setFont(font2)
        self.label_5.setStyleSheet(u"font-size:10pt;\n"
"background-color: rgb(255, 255, 255);")
        self.label_5.setFrameShape(QFrame.NoFrame)
        self.label_5.setFrameShadow(QFrame.Sunken)
        self.label_5.setLineWidth(2)
        self.label_5.setMidLineWidth(2)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.label_5)

        self.pushButton = QPushButton(self.frame_3)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QSize(200, 30))
        self.pushButton.setMaximumSize(QSize(200, 35))
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton.setFocusPolicy(Qt.NoFocus)
        self.pushButton.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/icon/facture-dachat.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton.setIcon(icon1)
        self.pushButton.setIconSize(QSize(20, 20))

        self.horizontalLayout_4.addWidget(self.pushButton, 0, Qt.AlignRight)


        self.verticalLayout.addWidget(self.frame_3)


        self.retranslateUi(Ui_payereste)

        QMetaObject.connectSlotsByName(Ui_payereste)
    # setupUi

    def retranslateUi(self, Ui_payereste):
        Ui_payereste.setWindowTitle(QCoreApplication.translate("Ui_payereste", u"Paiement", None))
        self.groupBox.setTitle(QCoreApplication.translate("Ui_payereste", u"Information sur la facture", None))
        self.lineEdit.setText("")
        self.label_9.setText("")
        self.montantRestantLineEdit.setText("")
        self.montantRestantLabel.setText(QCoreApplication.translate("Ui_payereste", u"Reste \u00e0 payer", None))
        self.label_4.setText("")
        self.label_3.setText(QCoreApplication.translate("Ui_payereste", u"Statut", None))
        self.montantPayLabel.setText(QCoreApplication.translate("Ui_payereste", u"Montant Pay\u00e9", None))
        self.dateLabel.setText(QCoreApplication.translate("Ui_payereste", u"Date de facturation", None))
        self.montantPayLineEdit.setText("")
        self.numeroFactureLineEdit.setText("")
        self.dateLineEdit.setText("")
        self.label_2.setText(QCoreApplication.translate("Ui_payereste", u"Mntant TTC", None))
        self.label_7.setText(QCoreApplication.translate("Ui_payereste", u"Client/ Fournisseur", None))
        self.numeroFactureLabel.setText(QCoreApplication.translate("Ui_payereste", u"Num\u00e9ro Facture", None))
        self.montantTotalLabel.setText(QCoreApplication.translate("Ui_payereste", u"Montant TH", None))
        self.montantTotalLineEdit.setText("")
        self.groupBox_2.setTitle(QCoreApplication.translate("Ui_payereste", u"Information Paiement", None))
        self.label_12.setText(QCoreApplication.translate("Ui_payereste", u"R\u00e9f\u00e9rence transaction", None))
        self.label_11.setText(QCoreApplication.translate("Ui_payereste", u"Date de paiement", None))
        self.reglELeResteLabel.setText(QCoreApplication.translate("Ui_payereste", u"Montant vers\u00e9", None))
        self.label_10.setText(QCoreApplication.translate("Ui_payereste", u"Mode de paiement", None))
        self.label_13.setText(QCoreApplication.translate("Ui_payereste", u"Compte de destination", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Ui_payereste", u"Esp\u00e8ces", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Ui_payereste", u"Ch\u00e8que", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Ui_payereste", u"Virement bancaire", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("Ui_payereste", u"Mobile money", None))
        self.comboBox.setItemText(4, QCoreApplication.translate("Ui_payereste", u"Carte bancaire", None))

        self.dateEdit.setDisplayFormat(QCoreApplication.translate("Ui_payereste", u"yyyy-MM-dd", None))
        self.label.setText("")
        self.label_8.setText("")
        self.label_5.setText("")
        self.pushButton.setText(QCoreApplication.translate("Ui_payereste", u"Valider", None))
    # retranslateUi

