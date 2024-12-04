from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class BoundaryOptions():
    def __init__(self, main):

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.frame.setLayout(self.layout)

        self.header = QtWidgets.QLabel("Boundary options")
        self.layout.addWidget(self.header)

        self.type_label = QtWidgets.QLabel("Selection")
        self.layout.addWidget(self.type_label)

        self.type = QtWidgets.QComboBox()
        self.type.addItem("Coastline")
        self.type.addItem("Lake")
        self.layout.addWidget(self.type)

        self.generate_button = QtWidgets.QPushButton("Generate boundary")
        self.generate_button.clicked.connect(main.generate_coastline)
        self.layout.addWidget(self.generate_button)

        self.layout.addStretch()
