from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QEvent, QTimer, Qt
from PyQt5.QtGui import QColor
from world import World
from plate_options import PlateOptions
from continent_options import ContinentOptions
from region import Region
from plate import Plate
import constants


class Main(QtWidgets.QMainWindow):
    # 1-RED, 5-BLUE, 10-GREEN, 13-YELLOW, 3-PURPLE, 6-LIGHTBLUE, 9-SEAGREEN
    # 12-OLIVE, 15-ORANGE, 17-BROWN, 18-BLUEGRAY, 2-MAGENTA, 8-TEAL, 11-GRASS
    # 14-LIGHTORANGE, 16-LIGHTRED
    PLATE_COLORS = [QColor(244, 67, 54), QColor(229, 115, 115),
                    QColor(63, 81, 181), QColor(121, 134, 203),
                    QColor(76, 175, 80), QColor(129, 199, 132),
                    QColor(255, 235, 59), QColor(255, 241, 118),
                    QColor(156, 39, 176), QColor(186, 104, 200),
                    QColor(33, 150, 243), QColor(100, 181, 246),
                    QColor(205, 220, 57), QColor(220, 231, 117),
                    QColor(255, 152, 0), QColor(255, 183, 77),
                    QColor(121, 85, 72), QColor(161, 136, 127),
                    QColor(96, 125, 139), QColor(144, 164, 174),
                    QColor(233, 30, 99), QColor(240, 98, 146),
                    QColor(0, 188, 212), QColor(77, 208, 225),
                    QColor(139, 195, 74), QColor(174, 213, 129),
                    QColor(255, 193, 7), QColor(255, 213, 79),
                    QColor(255, 87, 34), QColor(255, 138, 101)]

    def __init__(self):
        super().__init__()

        self.precision = constants.SUBREGION
        self.timer = QTimer()
        self.world = World(radius=6372, length=72, height=36)
        self.show_plate_borders: bool = True
        self.show_coordinate_lines: bool = True
        self.selected_plate: Plate = None

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
        self.continent_options = ContinentOptions(self, self.info_layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.view_world_info()

    def paint_plates(self):
        """Paints tectonic plates. Unclaimed regions are painted black"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        painter.fillRect(0, 0, 1440, 720, Qt.black)

        if self.precision == constants.SUBREGION:
            length = self.world.sub_length
        else:
            length = self.world.length

        point = 1440 // length
        pen.setWidth(point)

        for plate in self.world.plates:
            pen.setColor(Main.PLATE_COLORS[plate.id * 2])
            painter.setPen(pen)

            for region in plate.claimed_regions:
                painter.drawPoint(point//2 + region.x*point,
                                  point//2 + region.metrics.y*point)

            pen.setColor(Main.PLATE_COLORS[plate.id * 2 + 1])
            painter.setPen(pen)

            for region in plate.queued_regions:
                painter.drawPoint(point//2 + region.x*point,
                                  point//2 + region.metrics.y*point)
        painter.end()
        self.update()

    def has_plate_border(self, map: list[Region], region: Region, x: int, y: int,
                         dir: int) -> bool:
        """Returns true if the region has a plate border with an adjacent region"""
        # I could use instance variables of regions instead
        # It only works for subregions though
        # I need a solution for regions
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

            self.world.find_plate_boundaries()
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

        self.plate_options.generate_button.setEnabled(False)

        if self.plate_options.high_resolution.isChecked():
            self.precision = constants.SUBREGION
            world_map = self.world.subregions
            min_growth = self.plate_options.min_growth.value()*4
            max_growth = self.plate_options.max_growth.value()*4
            super_growth = 32
        else:
            self.precision = constants.REGION
            world_map = self.world.regions
            min_growth = self.plate_options.min_growth.value()
            max_growth = self.plate_options.max_growth.value()
            super_growth = 8

        if self.plate_options.supercontinent_toggle.isChecked():
            supercontinents = 1
        else:
            supercontinents = 0

        if self.plate_options.algorithm.currentText() == "Fixed growth":
            fixed_growth = True
        else:
            fixed_growth = False

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
            world_map=world_map,
            fixed_growth=fixed_growth)
        self.timer.singleShot(200, self.expand_plates)

    def add_plate_type(self):
        """Creates land using selected plate type and sea margin.
        Existing land is retained"""
        type = constants.get_type_value(
            self.continent_options.type.currentText())
        self.selected_plate.margin = self.continent_options.plate_margin.value()
        self.selected_plate.type = type
        self.selected_plate.create_land()
        self.view_continents()

    def set_plate_type(self):
        """Creates land using selected plate type and sea margin.
        Existing land is deleted"""
        type = constants.get_type_value(
            self.continent_options.type.currentText())
        self.selected_plate.margin = self.continent_options.plate_margin.value()
        self.selected_plate.type = type
        self.selected_plate.sink()
        self.selected_plate.create_land()
        self.view_continents()

    def create_mountains_on_land(self):
        for region in self.selected_plate.find_boundary_offset(0, constants.LAND):
            if region.terrain == constants.LAND:
                region.terrain = constants.MOUNTAIN
        self.view_continents()

    def create_mountains_by_sea(self):
        offset = self.continent_options.mountain_offset.value()
        for region in self.selected_plate.find_boundary_offset(offset, constants.WATER):
            if region.terrain == constants.LAND:
                region.terrain = constants.MOUNTAIN
        self.view_continents()

    def view_plates(self):
        """Paints the plates"""
        self.paint_plates()
        self.paint_lines()

    def view_continents(self):
        """Paints the world map"""
        self.paint_world()
        self.paint_grid()
        self.paint_lines()

    def view_world_info(self):
        """Shows world information"""
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
                self.selected_plate = self.world.get_plate(
                    column, row, constants.REGION)
                self.continent_options.type.setCurrentIndex(
                    self.selected_plate.type)
                self.continent_options.plate_margin.setValue(
                    self.selected_plate.margin)
                self.info_label.setText(
                    f"{header}\n{region.get_info()}\n\n{self.selected_plate.get_info()}")
            except IndexError:
                self.info_label.setText(f"{header}\n{region.get_info()}")

        return super().eventFilter(object, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Main()
    window.show()
    app.exec_()
