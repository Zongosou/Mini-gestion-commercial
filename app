from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStyle, QStyleFactory,
    QListWidget, QListWidgetItem, QSizePolicy, QSpacerItem,
    QStackedWidget
)
from PySide6.QtGui import QIcon

from fonction.TresorerieDash import SuiviTresorerie
from piece.piece_liste_patched import ListePiece
from stock.gest_stock import StockApp
from interface.icon_rc import *
import os
# ---------------------------
# Données fictives de stock
# ---------------------------

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/stock.db'))
class StockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GsCom - Gestion Commerciale")
        self.setWindowIcon(QIcon(":/icon/icone.png"))
        # Taille adaptée : par exemple 80% de l'écran
        screen = QApplication.primaryScreen()
        size = screen.availableGeometry()
        w = int(size.width() * 0.9)
        h = int(size.height() * 0.8)
        self.resize(w, h)
        
        # Centrer la fenêtre
        frame_geo = self.frameGeometry()
        center_point = screen.availableGeometry().center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        # Root container
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(root)
        # Content area
        self.app_content = QStackedWidget()
        # Sidebar
        sidebar = self._create_sidebar()
        root_layout.addWidget(sidebar)

        # Main content
        self.app_stoct = StockApp(db_connection=db_path,titre="Gestion de Stock")
        self.app_content.addWidget(self.app_stoct)  
        self.app_pices  = ListePiece(db_path)
        self.app_content.addWidget(self.app_pices)

        self.app_caisse = SuiviTresorerie(db_path)
        self.app_content.addWidget(self.app_caisse)
        root_layout.addWidget(self.app_content, 1)

        # Styles
        self._apply_styles()

     
    #  Connexions
        sidebar_widget = sidebar.findChild(QListWidget, "NavList")
        sidebar_widget.currentRowChanged.connect(self.app_content.setCurrentIndex)
    # ---------------------------
    # UI Builders
    # ---------------------------
    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # App logo / title
        app_title = QLabel("Gestion\nCommerciale")
        app_title.setObjectName("AppTitle")
        layout.addWidget(app_title)

        # Navigation
        nav = QListWidget()
        nav.setObjectName("NavList")
        nav.setSpacing(8)
        nav.setFrameShape(QFrame.Shape.NoFrame)
        nav.setStyleSheet("QListWidget::item { height: 42px; }")
        style = QApplication.style()

        items = [
            ("Stock", QIcon(":/icon/article.png")),
            ("Gestion des ventes", QIcon(":/icon/facture_achat.png")),
            ("Gestion des caisses", QIcon(":/icon/point-of-sale.png")),
        ]
        for text, icon in items:
            it = QListWidgetItem(icon, text)
            nav.addItem(it)
        nav.setCurrentRow(0)
        layout.addWidget(nav)
        # Spacer
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        # Settings/help
        btn_settings = QPushButton("Paramètres")
        btn_settings.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        btn_settings.setObjectName("SidebarButton")
        btn_help = QPushButton("Aide")
        btn_help.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        btn_help.setObjectName("SidebarButton")
        layout.addWidget(btn_settings)
        layout.addWidget(btn_help)
        return sidebar
    # ---------------------------
    # Styles
    # ---------------------------
    def _apply_styles(self):
        with open("config/style.qss", "r", encoding="utf-8") as f:
            style = f.read()
            self.setStyleSheet(style)

if __name__ == "__main__":
    app = QApplication([])
    win = StockWindow()
    win.show()
    app.exec()
