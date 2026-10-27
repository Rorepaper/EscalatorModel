from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit, \
    QLabel
from PyQt6.QtCore import pyqtSignal


class ParamsDialog(QDialog):
    accepted = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.setWindowTitle('Параметры эскалатора')

        self.input1 = QLineEdit('10000')  # интенсивность
        self.input2 = QLineEdit('0.4')  # доля идущих

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self._on_accept)
        self.buttonBox.rejected.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Интенсивность потока (чел/час):'))
        layout.addWidget(self.input1)
        layout.addWidget(QLabel('Доля идущих (0..1):'))
        layout.addWidget(self.input2)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def _on_accept(self):
        self.accepted.emit({
            'lam': float(self.input1.text()),
            'P_walk': float(self.input2.text())
        })
        self.close()