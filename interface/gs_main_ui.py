
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QListWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QFrame, QMenuBar, QSizePolicy
)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1250, 625)
        MainWindow.setWindowTitle("GSCom - Gestion commerciale")
        # Central widget
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.central_layout = QVBoxLayout(self.centralwidget)
        self.central_layout.setContentsMargins(8, 8, 8, 8)
        self.central_layout.setSpacing(6)

        # Top frame (placeholder)
        self.top_frame = QFrame(self.centralwidget)
        self.top_frame.setObjectName("top_frame")
        self.top_frame.setMaximumHeight(60)
        self.central_layout.addWidget(self.top_frame)

        # Main content frame
        self.main_frame = QFrame(self.centralwidget)
        self.main_layout = QHBoxLayout(self.main_frame)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(4)

        # Left menu (QListWidget)
        self.listWidget = QListWidget(self.main_frame)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setMinimumWidth(220)
        self.listWidget.setMaximumWidth(300)
        self.listWidget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding))
        self.main_layout.addWidget(self.listWidget)

        # Central stacked widget
        self.stackedWidget = QStackedWidget(self.main_frame)
        self.stackedWidget.setObjectName("stackedWidget")
        self.main_layout.addWidget(self.stackedWidget, 1)

        self.central_layout.addWidget(self.main_frame, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        # Menu bar (minimal)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        # Light theme base stylesheet placeholder (to be set by main)
        # end setupUi
