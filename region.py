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

        self.update_subdivision: bool = False

        # Plate belonging
        self.plate: int = -1

        # Variables used by plate
        self.plate_x: int = 0
        self.plate_y: int = 0
        self.border_distance: int = -1
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

    def has_boundary_at(self, direction: int) -> bool:
        """Returns true if the region in the given direction
        belongs to a different plate"""
        if direction == constants.NORTH:
            return self.north_boundary
        elif direction == constants.EAST:
            return self.east_boundary
        elif direction == constants.SOUTH:
            return self.south_boundary
        elif direction == constants.WEST:
            return self.west_boundary
        else:
            return False

    def is_boundary(self):
        """Returns true if this region is at a plate boundary"""
        return (self.north_boundary or self.east_boundary
                or self.south_boundary or self.west_boundary)

    def set_terrain(self, terrain: int, set_update_flag: bool = True) -> None:
        """Sets the regions terrain.
        If set_update_flag is true, the same terrain should be applied
        to smaller-sized areas belonging to this region.
        This function will not set the terrain of those areas."""
        self.terrain = terrain
        self.update_subdivision = set_update_flag

    def get_info(self) -> str:
        text = f"""Latitude: {self.metrics.south} to {self.metrics.north}
Longitude: {self.west} to {self.east}
Length: {self.metrics.top_stretch:,} to {self.metrics.bottom_stretch:,} km
Height: {self.metrics.vertical_stretch:,} km
Area: {self.metrics.area:,} km2
Cost: {self.metrics.cost:.4}"""
        return text
