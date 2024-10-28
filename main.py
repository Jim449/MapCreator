from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor
from world import World
import constants

# The continents still look a bit whacky,
# especially the ones crossing the east-west-barrier
# I may want to do some error searching
# Right! I still get the wrong coordinate from region in plate.expand
# Looking better
# Now, try showing some plate info when clicking on map


class Main(QtWidgets.QMainWindow):
    OCEAN = QColor(22, 134, 174)
    LAND = QColor(189, 171, 123)
    MOUNTAIN = QColor(237, 246, 247)
    SHALLOWS = QColor(110, 154, 174)
    SHALLOWS_2 = QColor(66, 144, 174)

    def __init__(self):
        super().__init__()

        self.world = World(radius=6372, length=72, height=36)

        self.layout = QtWidgets.QHBoxLayout()
        self.info_layout = QtWidgets.QVBoxLayout()
        self.map_layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.info_layout)
        self.layout.addLayout(self.map_layout)

        self.screen = QtWidgets.QLabel(parent=self)
        self.screen.installEventFilter(self)
        # World map has 72x36 regions and 360x180 subregions
        # Multiply the latter by 4 to get a decent display size
        self.world_map = QtGui.QPixmap(1440, 720)
        self.world_map.fill(Main.OCEAN)
        self.screen.setPixmap(self.world_map)
        self.map_layout.addWidget(self.screen)

        self.info_label = QtWidgets.QLabel("", self)
        self.info_layout.addWidget(self.info_label)

        self.world_create_button = QtWidgets.QPushButton(
            text="Generate world", parent=self)
        self.world_create_button.clicked.connect(self.generate_world)
        self.map_layout.addWidget(self.world_create_button)

        # Might be fun to see plates pop up and grow but I can do it faster with generate world

        # self.plate_create_button = QtWidgets.QPushButton(
        #     text="Create plates", parent=self)
        # self.plate_create_button.clicked.connect(self.create_plates)
        # self.map_layout.addWidget(self.plate_create_button)

        # self.plate_expand_button = QtWidgets.QPushButton(
        #     text="Expand plates", parent=self)
        # self.plate_expand_button.clicked.connect(self.expand_plates)
        # self.map_layout.addWidget(self.plate_expand_button)

        # self.continent_button = QtWidgets.QPushButton(
        #     text="Generate continents", parent=self)
        # self.continent_button.clicked.connect(self.create_continents)
        # self.map_layout.addWidget(self.continent_button)

        self.plate_view_button = QtWidgets.QPushButton(
            text="Show plates", parent=self)
        self.plate_view_button.clicked.connect(self.view_plates)
        self.map_layout.addWidget(self.plate_view_button)

        self.continent_view_button = QtWidgets.QPushButton(
            text="Show continents", parent=self)
        self.continent_view_button.clicked.connect(self.view_continents)
        self.map_layout.addWidget(self.continent_view_button)

        self.world_info_button = QtWidgets.QPushButton(
            text="Show world info", parent=self)
        self.world_info_button.clicked.connect(self.view_world_info)
        self.map_layout.addWidget(self.world_info_button)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def paint_plates(self):
        color_list = [QColor(180, 30, 30), QColor(30, 180, 30), QColor(30, 30, 180),
                      QColor(180, 120, 30), QColor(
                          30, 180, 120), QColor(120, 30, 180),
                      QColor(180, 30, 120), QColor(120, 180, 30), QColor(30, 120, 180)]
        black = QColor(0, 0, 0)
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(20)

        for y in range(self.world.height):
            for x in range(self.world.length):
                region = self.world.regions[y][x]
                if region.plate == -1:
                    pen.setColor(black)
                else:
                    pen.setColor(color_list[region.plate])
                painter.setPen(pen)
                painter.drawPoint(10+x*20, 10+y*20)
        painter.end()
        self.update()

    def paint_world(self):
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(20)
        outliner = QtGui.QPen()
        outliner.setWidth(1)
        outliner.setColor(QColor(0, 0, 0))

        for y in range(self.world.height):
            for x in range(self.world.length):
                region = self.world.regions[y][x]

                if region.terrain == constants.WATER:
                    pen.setColor(Main.OCEAN)
                elif region.terrain == constants.LAND:
                    pen.setColor(Main.LAND)
                elif region.terrain == constants.MOUNTAIN:
                    pen.setColor(Main.MOUNTAIN)
                elif region.terrain == constants.SHALLOWS:
                    pen.setColor(Main.SHALLOWS)
                elif region.terrain == constants.SHALLOWS_2:
                    pen.setColor(Main.SHALLOWS_2)
                painter.setPen(pen)
                painter.drawPoint(10+x*20, 10+y*20)

                if region.east_outline:
                    painter.setPen(outliner)
                    painter.drawLine(-1+(x+1)*20, -1+y*20,
                                     -1+(x+1)*20, -1+(y+1)*20)
                if region.south_outline:
                    painter.setPen(outliner)
                    painter.drawLine(-1+x*20, -1+(y+1)*20,
                                     -1+(x+1)*20, -1+(y+1)*20)
        painter.end()
        self.update()

    def create_plates(self):
        self.world.create_plates(6, 1)
        self.paint_plates()

    def expand_plates(self):
        self.world.build_plates()
        self.paint_plates()

    def create_continents(self):
        self.world.create_continents()
        self.world.find_outlines()
        self.paint_world()

    def generate_world(self):
        # Does the combined work of create_plates, expand_plates and create_continents
        self.world.create_plates(6, 1)
        self.world.build_plates()
        self.world.create_continents()
        self.world.find_outlines()
        self.paint_world()

    def view_plates(self):
        self.paint_plates()

    def view_continents(self):
        self.paint_world()

    def view_world_info(self):
        sea_area = self.world.get_sea_area()

        self.info_label.setText(f"""World
Area: {self.world.area:,} km2
Circumference: {self.world.circumference:,} km
Radius: {self.world.radius} km
Land: {self.world.get_land_area():,} km2
Sea: {sea_area:,} km2
Sea percentage: {sea_area / self.world.area:.0%}
""")

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonPress:
            x = event.x()
            y = event.y()
            column = x // 20
            row = y // 20
            plate = self.world.get_plate(column, row)
            self.info_label.setText(f"""Region at ({column}, {row})
Plate {plate.id}
Type: {constants.get_type(plate.type)}
Area: {plate.area:,} km2
Land area: {plate.land_area:,} km2
Sea area {plate.sea_area:,} km2
Sea percentage: {plate.sea_area / plate.area:.0%}
West end: {min(plate.west_end.values()) * 5}
East end: {max(plate.east_end.values()) * 5}
North end: {min(plate.north_end.values()) * 5}
South end: {max(plate.south_end.values()) * 5}
Growth: {plate.growth}
Sea margin: {plate.margin:.0%}
""")
        return super().eventFilter(object, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Main()
    window.show()
    app.exec_()

    # This all works fine...
    # map_creator: MapCreator = MapCreator(radius=6372, length=72, height=36)

    # world = map_creator.world
    # print(f"World, radius {world.radius:,}, circumference {
    #       world.circumference:,}, area {world.area:,}\n")

    # for circle in world.regions:
    #     region = circle[0]

    #     print(f"Region at {region.y}-{region.y+1}, widths {region.top_circle_width}-{
    #           region.bottom_circle_width}, height {region.circle_height}, area {
    #               region.area:,}, cost {region.cost}")
