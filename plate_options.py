from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class PlateOptions():
    def __init__(self, main, layout: QtWidgets.QVBoxLayout):

        self.header = QtWidgets.QLabel("Tectonic plate options")
        layout.addWidget(self.header)

        self.min_growth_label = QtWidgets.QLabel("Miniumum growth rate")
        layout.addWidget(self.min_growth_label)

        self.min_growth = QtWidgets.QSpinBox()
        self.min_growth.setMinimum(1)
        self.min_growth.setMaximum(8)
        self.min_growth.setValue(4)
        layout.addWidget(self.min_growth)

        self.max_growth_label = QtWidgets.QLabel("Maximum growth rate")
        layout.addWidget(self.max_growth_label)

        self.max_growth = QtWidgets.QSpinBox()
        self.max_growth.setMinimum(1)
        self.max_growth.setMaximum(8)
        self.max_growth.setValue(4)
        layout.addWidget(self.max_growth)

        self.land_plate_label = QtWidgets.QLabel(
            "Amount of continental plates")
        layout.addWidget(self.land_plate_label)

        self.land_plates = QtWidgets.QSpinBox()
        self.land_plates.setMinimum(1)
        self.land_plates.setMaximum(12)
        self.land_plates.setValue(7)
        layout.addWidget(self.land_plates)

        self.sea_plate_label = QtWidgets.QLabel("Amount of oceanic plates")
        layout.addWidget(self.sea_plate_label)

        self.sea_plates = QtWidgets.QSpinBox()
        self.sea_plates.setMinimum(0)
        self.sea_plates.setMaximum(11)
        self.sea_plates.setValue(1)
        layout.addWidget(self.sea_plates)

        self.supercontinent_toggle = QtWidgets.QCheckBox("Add supercontinent")
        layout.addWidget(self.supercontinent_toggle)

        self.plate_margin_label = QtWidgets.QLabel(
            "Sea margin of continental plates")
        layout.addWidget(self.plate_margin_label)

        self.plate_margin = QtWidgets.QDoubleSpinBox()
        self.plate_margin.setMinimum(0.1)
        self.plate_margin.setMaximum(0.4)
        self.plate_margin.setSingleStep(0.05)
        self.plate_margin.setValue(0.25)
        layout.addWidget(self.plate_margin)

        self.island_rate_label = QtWidgets.QLabel("Island rate")
        layout.addWidget(self.island_rate_label)

        self.island_rate = QtWidgets.QDoubleSpinBox()
        self.island_rate.setMinimum(0)
        self.island_rate.setMaximum(0.25)
        self.island_rate.setSingleStep(0.01)
        self.island_rate.setValue(0.01)
        layout.addWidget(self.island_rate)

        self.high_resolution = QtWidgets.QCheckBox("High resolution")
        self.high_resolution.click()
        layout.addWidget(self.high_resolution)

        self.generate_button = QtWidgets.QPushButton("Generate world")
        self.generate_button.clicked.connect(main.generate_world)
        layout.addWidget(self.generate_button)

        layout.addStretch()
