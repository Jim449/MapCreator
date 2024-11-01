from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QEvent, QTimer, Qt
from PyQt5.QtGui import QColor
from world import World
from plate_options import PlateOptions
from region import Region
import constants


class Main(QtWidgets.QMainWindow):

    PLATE_COLORS = [QColor(180, 30, 30), QColor(30, 180, 30), QColor(30, 30, 180),
                    QColor(180, 120, 30), QColor(
                        30, 180, 120), QColor(120, 30, 180),
                    QColor(180, 30, 120), QColor(
                        120, 180, 30), QColor(30, 120, 180),
                    QColor(180, 30, 180), QColor(180, 180, 30), QColor(30, 180, 180)]

    def __init__(self):
        super().__init__()

        self.precision = constants.SUBREGION
        self.timer = QTimer()

        self.world = World(radius=6372, length=72, height=36)
        self.show_plate_borders: bool
        self.show_coordinate_lines: bool

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.info_layout = QtWidgets.QVBoxLayout()
        self.info_layout.setSpacing(5)
        self.info_layout.setContentsMargins(5, 5, 5, 5)

        self.map_layout = QtWidgets.QVBoxLayout()
        self.map_layout.setSpacing(5)
        self.map_layout.setContentsMargins(5, 5, 5, 5)

        self.plate_option_layout = QtWidgets.QVBoxLayout()
        self.plate_option_layout.setSpacing(5)
        self.plate_option_layout.setContentsMargins(5, 5, 5, 5)

        self.layout.addLayout(self.info_layout)
        self.layout.addLayout(self.map_layout)
        self.layout.addLayout(self.plate_option_layout)

        self.screen = QtWidgets.QLabel(parent=self)
        self.screen.installEventFilter(self)
        # World map has 72x36 regions and 360x180 subregions
        # Multiply the latter by 4 to get a decent display size

        # I should have a zoomed in map as well
        # Maximum region size is 556x556 km
        # I can afford 1px per km
        # That should suffice

        # Use a medium zoom map too
        # I may want to display subregions at 20x20px
        # Then a region will be 100x100px
        # I can fit 14x7 regions

        self.world_map = QtGui.QPixmap(1440, 720)
        self.world_map.fill(constants.get_color(constants.WATER))
        self.screen.setPixmap(self.world_map)
        self.map_layout.addWidget(self.screen)

        self.info_label = QtWidgets.QLabel("", self)
        self.info_layout.addWidget(self.info_label)
        self.info_layout.addStretch()

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
        self.map_layout.addStretch()

        self.plate_options = PlateOptions(self, self.plate_option_layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.view_world_info()

    def paint_plates(self):
        """Paints tectonic plates. Unclaimed regions are painted black"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()

        if self.precision == constants.SUBREGION:
            map = self.world.subregions
            length = self.world.sub_length
            height = self.world.sub_height
        else:
            map = self.world.regions
            length = self.world.length
            height = self.world.height

        point = 1440 // length
        pen.setWidth(point)

        for y in range(height):
            for x in range(length):
                region = map[y][x]
                if region.plate == -1:
                    pen.setColor(Qt.black)
                else:
                    pen.setColor(Main.PLATE_COLORS[region.plate])

                painter.setPen(pen)
                painter.drawPoint(point//2 + x*point, point//2 + y*point)
        painter.end()
        self.update()

    def has_plate_border(self, map: list[Region], region: Region, x: int, y: int,
                         dir: int) -> bool:
        """Returns true if the region has a plate border with an adjacent region"""
        nx, ny = constants.get_next_coordinates(x, y, dir)

        try:
            return region.plate != map[ny][nx].plate
        except IndexError:
            return False

    def paint_world(self):
        """Paints regions or subregions"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()

        if self.precision == constants.SUBREGION:
            map = self.world.subregions
            length = self.world.sub_length
            height = self.world.sub_height
        else:
            map = self.world.regions
            length = self.world.length
            height = self.world.height

        point = 1440 // length
        pen.setWidth(point)

        outliner = QtGui.QPen()
        outliner.setWidth(1)
        outliner.setColor(constants.PLATE_BORDER_COLOR)

        for y in range(height):
            for x in range(length):
                region = map[y][x]
                pen.setColor(constants.get_color(region.terrain))
                painter.setPen(pen)
                painter.drawPoint(point//2 + x*point, point//2 + y*point)

                if self.has_plate_border(map, region, x, y, constants.EAST):
                    painter.setPen(outliner)
                    painter.drawLine((x+1)*point - 1, y*point - 1,
                                     (x+1)*point - 1, (y+1)*point - 1)

                if self.has_plate_border(map, region, x, y, constants.SOUTH):
                    painter.setPen(outliner)
                    painter.drawLine(x*point - 1, (y+1)*point - 1,
                                     (x+1)*point - 1, (y+1)*point - 1)
        painter.end()
        self.update()

    def paint_lines(self):
        """Draws lines at -60, -30, 0, 30, 60 latitude and -90, 0, 90 longitude"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        pen.setColor(constants.LINE_COLOR)
        painter.setPen(pen)
        painter.drawLine(0, 120, 1440, 120)
        painter.drawLine(0, 240, 1440, 240)
        painter.drawLine(0, 360, 1440, 360)
        painter.drawLine(0, 480, 1440, 480)
        painter.drawLine(0, 600, 1440, 600)
        painter.drawLine(360, 0, 360, 720)
        painter.drawLine(720, 0, 720, 720)
        painter.drawLine(1080, 0, 1080, 720)
        painter.end()
        self.update()

    def paint_grid(self):
        """Draws region grid"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        pen.setColor(constants.GRID_COLOR)
        painter.setPen(pen)

        for x in range(0, 1440, 20):
            for y in range(0, 720, 20):
                painter.drawLine(x, 0, x, 720)
                painter.drawLine(0, y, 1440, y)
        painter.end()
        self.update()

    def expand_plates(self):
        """Expands plates by one growth step and paints the progress.
        When finished, generates continents and paints the map"""
        if self.world.expand_plates():
            self.world.create_continents()

            if self.precision == constants.REGION:
                self.world.update_subregions_from_regions()
            else:
                self.world.update_regions_from_subregions()

            self.paint_world()
            self.paint_grid()
            self.paint_lines()
        elif self.precision == constants.REGION:
            self.paint_plates()
            self.timer.singleShot(500, self.expand_plates)
        elif self.precision == constants.SUBREGION:
            self.paint_plates()
            self.timer.singleShot(25, self.expand_plates)

    def generate_world(self):
        """Generates tectonic plates and creats continents"""

        if self.plate_options.high_resolution.isChecked():
            self.precision = constants.SUBREGION
            world_map = self.world.subregions
            min_growth = self.plate_options.min_growth.value()*4
            max_growth = self.plate_options.max_growth.value()*4
            super_growth = 32
        else:
            self.precision = Main.REGION
            world_map = self.world.regions
            min_growth = self.plate_options.min_growth.value()
            max_growth = self.plate_options.max_growth.value()
            super_growth = 8

        if self.plate_options.supercontinent_toggle.isChecked():
            supercontinents = 1
        else:
            supercontinents = 0

        # Needs to sink current plates if there are any
        self.world.create_plates(
            land_amount=self.plate_options.land_plates.value(),
            water_amount=self.plate_options.sea_plates.value(),
            margin=self.plate_options.plate_margin.value(),
            island_rate=self.plate_options.island_rate.value(),
            min_growth=min_growth,
            max_growth=max_growth,
            odd_amount=supercontinents,
            odd_growth=super_growth,
            world_map=world_map)
        self.timer.singleShot(200, self.expand_plates)

    def view_plates(self):
        self.paint_plates()
        self.paint_lines()

    def view_continents(self):
        self.paint_world()
        self.paint_grid()
        self.paint_lines()

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
        """Called on map click. Displays region or subregion information"""
        if event.type() == QEvent.MouseButtonPress:
            x = event.x()
            y = event.y()

            header = "Region"
            column = x // 20
            row = y // 20
            region = self.world.get_region(column, row)

            try:
                plate = self.world.get_plate(column, row, constants.REGION)
                self.info_label.setText(
                    f"{header}\n{region.get_info()}\n\n{plate.get_info()}")
            except IndexError:
                self.info_label.setText(f"{header}\n{region.get_info()}")

        return super().eventFilter(object, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Main()
    window.show()
    app.exec_()
