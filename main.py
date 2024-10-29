from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor
from world import World
from plate_options import PlateOptions
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
    PLATE_BORDER_COLOR = QColor(60, 15, 15)
    LINE_COLOR = QColor(15, 15, 60)

    def __init__(self):
        super().__init__()

        self.precision = "Region"

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
        self.world_map = QtGui.QPixmap(1440, 720)
        self.world_map.fill(Main.OCEAN)
        self.screen.setPixmap(self.world_map)
        self.map_layout.addWidget(self.screen)

        self.info_label = QtWidgets.QLabel("", self)
        self.info_layout.addWidget(self.info_label)
        self.info_layout.addStretch()

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

        self.plate_options = PlateOptions(self, self.plate_option_layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.view_world_info()

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

    def paint_subregions(self):
        painter = QtGui.QPainter(self.screen.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(4)

        for y in range(self.world.sub_height):
            for x in range(self.world.sub_length):
                region = self.world.get_subregion(x, y)

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
                painter.drawPoint(2+x*4, 2+y*4)
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
                region = self.world.get_region(x, y)

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
        self.world.create_plates(
            land_amount=self.land_plate_choice.value(),
            sea_amount=self.sea_plate_choice.value(),
            margin=self.plate_margin_choice.value(),
            island_rate=self.island_rate_choice.value(),
            growth=4)
        self.paint_plates()

    def expand_plates(self):
        self.world.build_plates()
        self.paint_plates()

    def create_continents(self):
        self.world.create_continents()
        self.world.find_outlines()
        self.paint_world()

    def generate_world(self):
        """Generates tectonic plates and creats continents"""
        # Does the combined work of create_plates, expand_plates and create_continents
        # So I can just scrap those buttons and methods
        self.world.create_plates(
            land_amount=self.plate_options.land_plates.value(),
            water_amount=self.plate_options.sea_plates.value(),
            margin=self.plate_options.plate_margin.value(),
            island_rate=self.plate_options.island_rate.value(),
            min_growth=self.plate_options.min_growth.value(),
            max_growth=self.plate_options.max_growth.value())
        # Growth should be adjustable by user
        # I wonder how I can go about doing that without adding a growth selector for each plate

        # Option 1: I establish standard growths small, medium, large = 4, 8, 12 or something like that
        # The user decides how many plates of each size he wants
        # So the continental plate amount button would split into three buttons for small, medium, large
        # Same for oceanic plates. That sounds like a lot of buttons!

        # Option 2: I create growth templates, like equal size, mini-plates and supercontinent
        # This sounds like it could become fun. Option 1 doesn't allow for supercontinents!
        # Go through the options...
        # Equal growth: everything gets growth 4
        # Mini-plates: About 20% gets growth 1, the rest gets growth 20
        # Varied: About 20% gets growth 4, 60% gets growth 8, 20% gets growth 12
        # Single-large: A single plate gets growth 8, the rest gets growth 4
        # Supercontinent: A single plate gets growth 8, the rest gets growth 1
        # (give the supercontinent the center type?)

        # Option 3: I actually let the user build a list. I'll need a button to summon a popup-window
        # It should hold a list of all plates growths
        # The user can select a plate and enter a new value
        # This would be more time-consuming to implement

        # Option 4: Use randomness. The user chooses minimum and maximum growth
        # Growth is selected uniformly from this range
        # Additional option: let the user select random distribution
        # An exponential random distribution should be selectable
        # Or a normal random distribution
        # This option sounds pretty good, I think
        # It doesn't require too many buttons
        # Uniform distribution may allow for mini-continents
        # Larger continents will have growth no more than 200% of medium sized ones
        # Normal distribution will not give much variety, I think
        # There's built-in variety so I may want distribution to do bolder stuff

        # Rather than sending a single growth value to world, I should send two lists
        # One for continental plates and one for oceanic plates
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

            if self.precision == "Region":
                column = x // 20
                row = y // 20
                region = self.world.get_region(column, row)
                try:
                    plate = self.world.get_plate(column, row)
                    self.info_label.setText(
                        "Region\n" + region.get_info() + "\n\n" + plate.get_info())
                except IndexError:
                    self.info_label.setText("Region\n" + region.get_info())
            elif self.precision == "Subregion":
                column = x // 4
                row = x // 4
                subregion = self.world.get_region(column, row)
                self.info_label.setText("Subregion\n" + subregion.get_info())

        return super().eventFilter(object, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Main()
    window.show()
    app.exec_()
