from area import Area
import constants


class Region(Area):
    """Represents an area of 5x5 lat x long, seperated into areas of 1x1 lat x long"""

    def __init__(self, x: int, y: int, top_circle_width: int, bottom_circle_width: int,
                 circle_height: int, area: int, cost: int):
        """Creates a region at coordinates (x,y)"""
        super().__init__()

        self.x: int = x
        self.y: int = y
        self.length: int = 5
        self.height: int = 5
        self.top_circle_width: int = top_circle_width
        self.bottom_circle_width: int = bottom_circle_width
        self.circle_height: int = circle_height
        self.area: int = area
        self.cost: float = cost
        self.plate: int = -1
        self.plate_x: int = 0
        self.plate_y: int = 0
        self.active: bool = True
        self.alive: bool = True
        self.horizontal_land_check = False
        self.vertical_land_check = False
        self.terrain = constants.WATER

        self.north_outline: bool = False
        self.east_outline: bool = False
        self.south_outline: bool = False
        self.west_outline: bool = False
