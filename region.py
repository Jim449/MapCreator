from area import Area
import constants


class Region(Area):
    """Represents an area on the globe, confined by longitude and latitude lines"""

    def __init__(self, x: int, y: int, side: int,
                 top_circle_width: int, bottom_circle_width: int,
                 circle_height: int, area: int, cost: int,
                 max_x: int, max_y: int):
        """Creates a region

        Args:
            x:
                x index
            y:
                y index
            side:
                lenght/height in longitude/latitude
            top_circle_width:
                globe distance km from northeast to northwest end
            bottom_circle_width:
                globe distance km from southeast to southwest end
            circle-height:
                globe distance km from north to south
            area:
                globe area km2
            cost:
                value relative to area, standardized to max 1
            max_x:
                max x index + 1
            max_y:
                max y index + 1
            """
        super().__init__()

        self.x: int = x
        self.y: int = y
        self.side: int = side
        self.west = round(x / max_x * 360 - 180)
        self.east = self.west + side
        self.north = round(-y / max_y * 180 + 90)
        self.south = self.north - side
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

    def get_info(self) -> str:
        text = f"""Latitude: {self.north} to {self.south}
Longitude: {self.west} to {self.east}
Length: {self.top_circle_width:,} to {self.bottom_circle_width:,} km
Height: {self.circle_height:,} km
Area: {self.area:,} km2"""
        return text
