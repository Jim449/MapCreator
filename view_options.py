from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class ViewOptions():
    """Options for changing map display"""

    def __init__(self, main):
        """Creates new view options with a vertical box layout"""
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # I believe the checkbox passed a boolean variable implicitly,
        # setting the details flag to false when checking off
        # A lambda should solve that so it's always True
        self.view_grid = QtWidgets.QCheckBox(text="View grid")
        self.view_grid.stateChanged.connect(lambda: main.view_continents(True))
        self.layout.addWidget(self.view_grid)

        self.view_lines = QtWidgets.QCheckBox(text="View key lines")
        self.view_lines.stateChanged.connect(
            lambda: main.view_continents(True))
        self.layout.addWidget(self.view_lines)

        self.view_plate_borders = QtWidgets.QCheckBox(
            text="View plate borders")
        self.view_plate_borders.stateChanged.connect(
            lambda: main.view_continents(True))
        self.layout.addWidget(self.view_plate_borders)

        self.view_world = QtWidgets.QPushButton(text="View world")
        self.view_world.clicked.connect(lambda: main.view_continents(True))
        self.layout.addWidget(self.view_world)

        self.layout.addStretch()
