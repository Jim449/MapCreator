from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class ToolInfo():
    """Displays a label. Use to prompt the user to select something on the map."""

    def __init__(self):
        """Creates a new, empty frame"""
        self.tool: str = None

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.frame.setLayout(self.layout)

        self.header = QtWidgets.QLabel()
        self.layout.addWidget(self.header)

    def set_text(self, text: str) -> None:
        """Sets the text of the label"""
        self.header.setText(text)

    def activate(self, tool: str) -> None:
        """Sets the current tool and reveals the frame"""
        self.tool = tool
        self.frame.show()

    def get_current_tool(self) -> str:
        """Gets the current tool"""
        return self.tool
