from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class ContinentOptions():
    def __init__(self, main):

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.frame.setLayout(self.layout)

        self.header = QtWidgets.QLabel("Continent options")
        self.layout.addWidget(self.header)

        self.type_label = QtWidgets.QLabel("Continent type")
        self.layout.addWidget(self.type_label)

        self.type = QtWidgets.QComboBox()
        self.type.addItem("Center")
        self.type.addItem("North")
        self.type.addItem("Northeast")
        self.type.addItem("East")
        self.type.addItem("Southeast")
        self.type.addItem("South")
        self.type.addItem("Southwest")
        self.type.addItem("West")
        self.type.addItem("Northwest")
        self.type.addItem("Land")
        self.type.addItem("Water")
        self.layout.addWidget(self.type)

        self.plate_margin_label = QtWidgets.QLabel("Sea margin")
        self.layout.addWidget(self.plate_margin_label)

        self.plate_margin = QtWidgets.QDoubleSpinBox()
        self.plate_margin.setMinimum(0.0)
        self.plate_margin.setMaximum(0.4)
        self.plate_margin.setSingleStep(0.05)
        self.plate_margin.setValue(0.20)
        self.layout.addWidget(self.plate_margin)

        self.add_button = QtWidgets.QPushButton("Add type")
        self.add_button.clicked.connect(main.add_plate_type)
        self.layout.addWidget(self.add_button)

        self.set_button = QtWidgets.QPushButton("Set type")
        self.set_button.clicked.connect(main.set_plate_type)
        self.layout.addWidget(self.set_button)

        self.mountain_label = QtWidgets.QLabel("Mountain ranges")
        self.layout.addWidget(self.mountain_label)

        self.land_mountain = QtWidgets.QPushButton("Generate by land")
        self.land_mountain.clicked.connect(main.create_mountains_on_land)
        self.layout.addWidget(self.land_mountain)

        self.mountain_offset_label = QtWidgets.QLabel("Distance to shore")
        self.layout.addWidget(self.mountain_offset_label)

        self.mountain_offset = QtWidgets.QSpinBox()
        self.mountain_offset.setMinimum(0)
        self.mountain_offset.setMaximum(20)
        self.mountain_offset.setSingleStep(1)
        self.mountain_offset.setValue(1)
        self.layout.addWidget(self.mountain_offset)

        self.sea_mountain = QtWidgets.QPushButton("Generate by sea")
        self.sea_mountain.clicked.connect(main.create_mountains_by_sea)
        self.layout.addWidget(self.sea_mountain)

        self.erase_mountain = QtWidgets.QPushButton("Erase mountains")
        self.erase_mountain.clicked.connect(main.erase_mountains)
        self.layout.addWidget(self.erase_mountain)

        self.layout.addStretch()
