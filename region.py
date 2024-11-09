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
        self.free: bool = True

        self.horizontal_land_check = False
        self.vertical_land_check = False
        self.ascending_land_check = False
        self.descending_land_check = False

        self.terrain = constants.WATER

    def get_info(self) -> str:
        text = f"""Latitude: {self.metrics.south} to {self.metrics.north}
Longitude: {self.west} to {self.east}
Length: {self.metrics.top_stretch:,} to {self.metrics.bottom_stretch:,} km
Height: {self.metrics.vertical_stretch:,} km
Area: {self.metrics.area:,} km2"""
        return text
