from PyQt6.QtWidgets import QWidget, QApplication
import sys
from MainW import Ui_Form


class TradeUI(QWidget, Ui_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.show()


app = QApplication(sys.argv)
BeginTDsys = TradeUI()
sys.exit(app.exec())
