from region_metrics import RegionMetrics
import constants


class Region():
    """Represents an area on the globe, confined by longitude and latitude lines"""

    def __init__(self, x: int, metrics: RegionMetrics):
        super().__init__()

        self.x: int = x
        self.metrics = metrics

        step = 360 // metrics.length_division
        self.west = x * step - 180
        self.east = self.west + step

        self.plate: int = -1
        self.plate_x: int = 0
        self.plate_y: int = 0
        self.active: bool = True

        self.horizontal_land_check = False
        self.vertical_land_check = False
        self.ascending_land_check = False
        self.descending_land_check = False

        self.terrain = constants.WATER

        self.north_boundary = False
        self.east_boundary = False
        self.south_boundary = False
        self.west_boundary = False

    def is_boundary(self):
        """Returns true if this region is at a plate boundary"""
        return (self.north_boundary or self.east_boundary
                or self.south_boundary or self.west_boundary)

    def get_info(self) -> str:
        text = f"""Latitude: {self.metrics.south} to {self.metrics.north}
Longitude: {self.west} to {self.east}
Length: {self.metrics.top_stretch:,} to {self.metrics.bottom_stretch:,} km
Height: {self.metrics.vertical_stretch:,} km
Area: {self.metrics.area:,} km2
Cost: {self.metrics.cost:.4}"""
        return text
