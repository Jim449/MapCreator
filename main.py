from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QEvent, QTimer, Qt
from PyQt5.QtGui import QColor
from world import World
from plate_options import PlateOptions
from continent_options import ContinentOptions
from boundary_options import BoundaryOptions
from view_options import ViewOptions
from tool_info import ToolInfo
from toolbar import Toolbar
from region import Region
from plate import Plate
import constants


class Main(QtWidgets.QMainWindow):
    # 1-RED, 5-BLUE, 10-GREEN, 13-YELLOW, 3-PURPLE, 6-LIGHTBLUE, 9-SEAGREEN
    # 15-ORANGE, 17-BROWN, 18-BLUEGRAY, 2-MAGENTA, 8-TEAL, 11-GRASS
    # 14-LIGHTORANGE, 16-LIGHTRED, 12-OLIVE
    PLATE_COLORS = [QColor(244, 67, 54), QColor(229, 115, 115),
                    QColor(63, 81, 181), QColor(121, 134, 203),
                    QColor(76, 175, 80), QColor(129, 199, 132),
                    QColor(255, 235, 59), QColor(255, 241, 118),
                    QColor(156, 39, 176), QColor(186, 104, 200),
                    QColor(33, 150, 243), QColor(100, 181, 246),
                    QColor(205, 220, 57), QColor(220, 231, 117),
                    QColor(121, 85, 72), QColor(161, 136, 127),
                    QColor(96, 125, 139), QColor(144, 164, 174),
                    QColor(233, 30, 99), QColor(240, 98, 146),
                    QColor(0, 188, 212), QColor(77, 208, 225),
                    QColor(139, 195, 74), QColor(174, 213, 129),
                    QColor(255, 193, 7), QColor(255, 213, 79),
                    QColor(255, 87, 34), QColor(255, 138, 101),
                    QColor(255, 152, 0), QColor(255, 183, 77)]

    # If one region contains 5 subregions, region size is 20,
    # region length is 72 and region height is 36
    # That's good but I'd like an even number (makes it easier when creating boundaries)
    # If one region contains 6 subregions, region size is 24
    # region length is 60 and region height is 30
    # Let's try it
    REGION_SIZE: int = 24
    REGION_LENGTH: int = 60
    REGION_HEIGHT: int = 30

    X_START: tuple[int] = (None, 0, 1, 1, 1, 1, 0, 0, 0)
    Y_START: tuple[int] = (None, 0, 0, 0, 1, 1, 1, 1, 0)
    X_END: tuple[int] = (None, 1, 1, 1, 1, 0, 0, 0, 0)
    Y_END: tuple[int] = (None, 0, 0, 1, 1, 1, 1, 0, 0)

    def __init__(self):
        super().__init__()

        self.precision = constants.SUBREGION
        self.timer = QTimer()
        self.world = World(
            radius=6372, length=Main.REGION_LENGTH, height=Main.REGION_HEIGHT)

        self.selected_plate: Plate = None
        self.selected_region: Region = None
        # Zoom level named from smallest visible area type
        self.zoom_level: str = constants.SUBREGION

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Info panel to the left
        self.info_layout = QtWidgets.QVBoxLayout()
        self.info_layout.setSpacing(5)
        self.info_layout.setContentsMargins(5, 5, 5, 5)
        self.info_label = QtWidgets.QLabel()
        self.info_layout.addWidget(self.info_label)
        self.info_layout.addStretch()

        # Map in the center
        self.map_layout = QtWidgets.QVBoxLayout()
        self.map_layout.setSpacing(5)
        self.map_layout.setContentsMargins(5, 5, 5, 5)

        self.screen = QtWidgets.QLabel(parent=self)
        self.screen.installEventFilter(self)
        self.world_map = QtGui.QPixmap(1440, 720)
        self.world_map.fill(constants.get_color(constants.WATER))
        self.screen.setPixmap(self.world_map)
        self.map_layout.addWidget(self.screen)

        # Options under the map
        self.options_layout = QtWidgets.QHBoxLayout()
        self.map_layout.addLayout(self.options_layout)

        self.toolbar = Toolbar(self)
        self.view_options = ViewOptions(self)

        self.options_layout.addLayout(self.toolbar.layout)
        self.options_layout.addLayout(self.view_options.layout)

        # Right panel - show a single panel, starting with plate generation
        self.tool_layout = QtWidgets.QVBoxLayout()

        self.plate_options = PlateOptions(self)
        self.continent_options = ContinentOptions(self)
        self.boundary_options = BoundaryOptions(self)
        self.tool_info = ToolInfo()

        self.tool_layout.addWidget(self.plate_options.frame)
        self.tool_layout.addWidget(self.continent_options.frame)
        self.tool_layout.addWidget(self.boundary_options.frame)
        self.tool_layout.addWidget(self.tool_info.frame)

        self.current_tool = self.plate_options
        self.continent_options.frame.hide()
        self.boundary_options.frame.hide()
        self.tool_info.frame.hide()

        # Add everything
        self.layout.addLayout(self.info_layout)
        self.layout.addLayout(self.map_layout)
        self.layout.addLayout(self.tool_layout)

        # Central widget to get things going
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

    def paint_edges(self, painter: QtGui.QPainter, x: int, y: int,
                    regions: list[Region], surrounding_terrain: int,
                    edge_color: QColor, width: int = 1) -> None:
        """Paints the edges of a subregion in the edge color
        if the subregion borders to the given terrain"""

        size = 1440 // self.world.sub_length
        pen = QtGui.QPen()
        pen.setWidth(width)
        pen.setColor(edge_color)
        painter.setPen(pen)

        for dir in range(1, 8, 2):
            if regions[dir] is not None and \
                    constants.is_type(regions[dir].terrain, surrounding_terrain):
                coordinates = constants.get_side(dir, width)
                painter.drawRect(x * size + coordinates[0], y * size + coordinates[1],
                                 coordinates[2], coordinates[3])

    def paint_corners(self, painter: QtGui.QPainter, x: int, y: int,
                      regions: list[Region], surrounding_terrain: int,
                      corner_color: QColor, corner_width: int = 1):
        """Paints the corner of a subregion in the corner color
        if the subregion borders to the given terrain on two sides"""
        size = 1440 // self.world.sub_length
        corner_pen = QtGui.QPen()
        corner_pen.setWidth(corner_width)
        corner_pen.setColor(corner_color)
        painter.setPen(corner_pen)

        for dir in range(1, 8, 2):
            next_dir = (dir + 2) % 8
            if regions[dir] is not None and regions[next_dir] is not None and \
                constants.is_type(regions[dir].terrain, surrounding_terrain) and \
                    constants.is_type(regions[next_dir].terrain, surrounding_terrain):
                coordinates = constants.get_corner(dir + 1)
                painter.drawPoint(x*size + coordinates[0],
                                  y*size + coordinates[1])

    def paint_diagonals(self, painter: QtGui.QPainter, x: int, y: int,
                        regions: list[Region], surrounding_terrain: int,
                        diagonal_color: QColor, diagonal_width: int = 1):
        diagonal_pen = QtGui.QPen()
        diagonal_pen.setWidth(diagonal_width)
        diagonal_pen.setColor(diagonal_color)
        center_terrain = regions[0].terrain
        painter.setPen(diagonal_pen)

        # TODO so I want to connect two diagonal tiles
        # I could draw a number of lines between them
        # If I could draw a tilted rectangle, that's even better
        # I may want to draw an outline in a different color
        # The results of paint_corners should be painted over
        # This method will paint on surrounding regions
        # It's important to call paint_diagonals last

    def paint_plate_borders(self) -> None:
        """Paints plate borders"""
        point = 1440 // self.world.sub_length
        painter = QtGui.QPainter(self.screen.pixmap())
        outliner = QtGui.QPen()
        outliner.setWidth(1)
        outliner.setColor(constants.PLATE_BORDER_COLOR)
        painter.setPen(outliner)

        for row in self.world.subregions:
            for subregion in row:
                if subregion.east_boundary:
                    painter.drawLine((subregion.x + 1) * point - 1,
                                     subregion.metrics.y * point,
                                     (subregion.x + 1) * point - 1,
                                     (subregion.metrics.y + 1) * point - 1)

                if subregion.south_boundary:
                    painter.drawLine(subregion.x * point,
                                     (subregion.metrics.y + 1) * point - 1,
                                     (subregion.x + 1) * point - 1,
                                     (subregion.metrics.y + 1) * point - 1)
        painter.end()

    def paint_world(self) -> None:
        """Paints regions or subregions"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        map = self.world.get_subregions_by_terrain()
        point = 1440 // self.world.sub_length
        pen.setWidth(point)

        for terrain, regions in map.items():
            pen.setColor(constants.get_color(terrain))
            painter.setPen(pen)

            for region in regions:
                painter.drawPoint(point//2 + region.x*point,
                                  point//2 + region.metrics.y*point)
        painter.end()

    def paint_details(self):
        painter = QtGui.QPainter(self.screen.pixmap())

        for row in self.world.subregions:
            for subregion in row:
                coordinates = constants.get_surroundings(
                    subregion.x, subregion.metrics.y,
                    self.world.sub_length, self.world.sub_height)
                surroundings = self.world.get_all_subregions(coordinates)

                if subregion.terrain == constants.LAND:
                    self.paint_edges(painter, subregion.x, subregion.metrics.y,
                                     surroundings, constants.WATER,
                                     edge_color=constants.get_color(
                                         constants.SHORE),
                                     width=2)
                    self.paint_corners(painter, subregion.x, subregion.metrics.y,
                                       surroundings, constants.WATER,
                                       constants.get_color(constants.SHALLOWS),
                                       2)
                elif subregion.terrain == constants.WATER:
                    self.paint_edges(painter, subregion.x, subregion.metrics.y,
                                     surroundings, constants.LAND,
                                     edge_color=constants.get_color(
                                         constants.SHALLOWS),
                                     width=2)
                    self.paint_corners(painter, subregion.x, subregion.metrics.y,
                                       surroundings, constants.LAND,
                                       constants.get_color(constants.SHORE),
                                       2)
                elif subregion.terrain == constants.MOUNTAIN:
                    self.paint_edges(painter, subregion.x, subregion.metrics.y,
                                     surroundings, constants.FLATLAND,
                                     edge_color=constants.get_color(
                                         constants.CLIFFS),
                                     width=1)
        painter.end()

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

    def paint_grid(self):
        """Draws region grid"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        pen.setColor(constants.GRID_COLOR)
        painter.setPen(pen)

        for x in range(0, 1440, Main.REGION_SIZE):
            for y in range(0, 720, Main.REGION_SIZE):
                painter.drawLine(x, 0, x, 720)
                painter.drawLine(0, y, 1440, y)
        painter.end()

    def paint_coastline(self, coastline: list[Region]):
        """Paints all regions in the coastline with diagonal lines"""
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        pen.setColor(constants.PLATE_BORDER_COLOR)
        painter.setPen(pen)

        for region in coastline:
            painter.drawLine(region.x * Main.REGION_SIZE,
                             region.metrics.y * Main.REGION_SIZE,
                             (region.x + 1) * Main.REGION_SIZE - 1,
                             (region.metrics.y + 1) * Main.REGION_SIZE - 1)
            painter.drawLine((region.x + 1) * Main.REGION_SIZE - 1,
                             region.metrics.y * Main.REGION_SIZE,
                             region.x * Main.REGION_SIZE,
                             (region.metrics.y + 1) * Main.REGION_SIZE - 1)
        painter.end()

    def paint_region_map(self, map: dict[list]):
        """Paints all square kilometers of a region"""
        painter = QtGui.QPainter(self.screen.pixmap())
        painter.fillRect(0, 0, 1440, 720, QColor(0, 0, 0))

        unique = set(map["terrain"])

        for terrain in unique:
            pen = QtGui.QPen()
            pen.setColor(constants.get_color(terrain))
            pen.setWidth(1)
            painter.setPen(pen)

            for i in range(len(map["x"])):
                painter.drawPoint(720 + map["x"][i], 26 + map["y"][i])
        painter.end()

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
            self.view_world_info()
            self.view_continents()

        elif self.precision == constants.REGION:
            self.paint_plates()
            self.timer.singleShot(100, self.expand_plates)
        elif self.precision == constants.SUBREGION:
            self.paint_plates()
            self.timer.singleShot(25, self.expand_plates)

    def generate_world(self):
        """Generates tectonic plates and creats continents"""

        self.plate_options.generate_button.setEnabled(False)
        self.toolbar.plate_generation_tool.setEnabled(False)

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
        self.world.update_regions_from_subregions()
        self.view_continents(detailed=False)

    def set_plate_type(self):
        """Creates land using selected plate type and sea margin.
        Existing land is deleted"""
        type = constants.get_type_value(
            self.continent_options.type.currentText())
        self.selected_plate.margin = self.continent_options.plate_margin.value()
        self.selected_plate.type = type
        self.selected_plate.sink()
        self.selected_plate.create_land()
        self.world.update_regions_from_subregions()
        self.view_continents(detailed=False)

    def create_mountains_on_land(self):
        """Creates mountain ranges on selected plate, where it meets a continental plate"""
        regions = self.selected_plate.find_border_offset(constants.LAND, constants.LAND,
                                                         1, 1)
        for region in regions:
            region.terrain = constants.MOUNTAIN
        self.view_continents(detailed=False)

    def create_mountains_by_sea(self):
        """Creates mountain ranges on selected plate, where it meets an oceanic plate"""
        min_offset = self.continent_options.min_offset.value()
        max_offset = self.continent_options.max_offset.value()
        regions = self.selected_plate.find_border_offset(constants.LAND, constants.WATER,
                                                         min_offset, max_offset)

        for region in regions:
            region.terrain = constants.MOUNTAIN

        self.view_continents(detailed=False)

    def erase_mountains(self):
        """Removes all mountains from the selected plate"""
        for region in self.selected_plate.claimed_regions:
            if region.terrain == constants.MOUNTAIN:
                region.terrain = constants.LAND
        self.view_continents(detailed=False)

    def open_plate_options(self):
        self.current_tool.frame.hide()
        self.plate_options.frame.show()
        self.current_tool = self.plate_options

    def open_continent_options(self):
        self.current_tool.frame.hide()
        self.continent_options.frame.show()
        self.current_tool = self.continent_options

    def open_boundary_options(self):
        self.current_tool.frame.hide()
        self.boundary_options.frame.show()
        self.boundary_options.generate_button.setEnabled(False)
        self.current_tool = self.boundary_options

    def full_zoom(self):
        """Prepares for a region full zoom"""
        self.current_tool.frame.hide()
        self.tool_info.set_text("Select the region to open")
        self.tool_info.activate("Open region")
        self.current_tool = self.tool_info

    def select_coastline(self, region: Region):
        """Selects a coastline"""
        coastline = self.world.find_region_coastline(
            region.x, region.metrics.y)
        self.boundary_options.generate_button.setEnabled(True)
        self.view_continents(detailed=False)
        self.paint_coastline(coastline)

    def generate_coastline(self):
        """Randomizes the selected coastline"""
        self.world.generate_region_coastline()
        self.view_continents(detailed=False)

    def view_plates(self):
        """Paints the plates"""
        self.paint_plates()
        if self.view_options.view_grid.isChecked():
            self.paint_grid()
        if self.view_options.view_lines.isChecked():
            self.paint_lines()
        self.update()

    def view_continents(self, detailed: bool = True):
        """Paints the world map"""
        self.zoom_level = constants.SUBREGION
        self.paint_world()

        if detailed:
            self.paint_details()
        if self.view_options.view_grid.isChecked():
            self.paint_grid()
        if self.view_options.view_lines.isChecked():
            self.paint_lines()
        if self.view_options.view_plate_borders.isChecked():
            self.paint_plate_borders()
        self.update()

    def view_square_kilometers(self, region: Region):
        """Zooms the region"""
        self.zoom_level = constants.SQUARE_KILOMETER
        self.world.construct_region(region.x, region.metrics.y)
        # Loops over a dict now. Don't try and loop over a dataframe, takes forever
        self.paint_region_map(self.world.km_squares_dicts)
        self.update()

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

            if self.zoom_level == constants.SUBREGION:
                header = "Region"
                column = x // Main.REGION_SIZE
                row = y // Main.REGION_SIZE

                self.selected_region = self.world.get_region(column, row)
                self.info_label.setText(
                    f"{header}\n{self.selected_region.get_info()}")

                try:
                    self.selected_plate = self.world.get_plate(
                        column, row, constants.REGION)
                except IndexError:
                    pass

                if self.current_tool == self.continent_options:
                    self.continent_options.type.setCurrentIndex(
                        self.selected_plate.type)
                    self.continent_options.plate_margin.setValue(
                        self.selected_plate.margin)
                    self.info_label.setText(
                        f"{header}\n{self.selected_region.get_info()}\n\n{self.selected_plate.get_info()}")

                elif self.current_tool == self.boundary_options:
                    self.select_coastline(self.selected_region)

                elif self.current_tool == self.tool_info:
                    if self.tool_info.get_current_tool() == "Open region":
                        self.view_square_kilometers(self.selected_region)

            elif self.zoom_level == constants.SQUARE_KILOMETER:
                # More options to come
                pass

        return super().eventFilter(object, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Main()
    window.show()
    app.exec_()
