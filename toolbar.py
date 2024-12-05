from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class Toolbar():
    def __init__(self, main):

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.plate_generation_tool = QtWidgets.QPushButton(
            text="Plate generation")
        self.layout.addWidget(self.plate_generation_tool)

        self.continent_tool = QtWidgets.QPushButton(text="Continent tools")
        self.continent_tool.clicked.connect(main.open_continent_options)
        self.layout.addWidget(self.continent_tool)

        self.boundary_tool = QtWidgets.QPushButton(text="Boundary tools")
        self.boundary_tool.clicked.connect(main.open_boundary_options)
        self.layout.addWidget(self.boundary_tool)

        self.plate_tool = QtWidgets.QPushButton(text="Paint plates")
        self.layout.addWidget(self.plate_tool)

        self.terrain_tool = QtWidgets.QPushButton(text="Paint terrain")
        self.layout.addWidget(self.terrain_tool)

        self.layout.addStretch()
