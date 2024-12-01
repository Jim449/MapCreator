from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class ContinentOptions():
    def __init__(self, main, layout: QtWidgets.QVBoxLayout):
        self.header = QtWidgets.QLabel("Region options")
        layout.addWidget(self.header)

        self.coastline_button = QtWidgets.QPushButton("Select coastline")
        self.coastline.clicked.connect(main.select_coastline)
        layout.addWidget(self.coastline_button)

        layout.addStretch()
