from area import Area
from region import Region
from subregion import Subregion
from plate import Plate
import constants
import math
import random


class World(Area):
    """Represents the world"""

    def __init__(self, radius: int = 6372, length: int = 72, height: int = 36):
        """Creates a new world, separated into regions.
        Length/height specify how many regions fit horizontally and vertically.
        Length should be twice the value of height in order to mimic longitude and latitude"""
        super().__init__()

        self.radius: int = radius
        self.circumference: int = int(2 * radius * math.pi)
        self.area: int = int(4 * math.pow(radius, 2) * math.pi)
        self.length = length
        self.height = height
        self.region_height: int = int(self.circumference / self.length)
        self.regions: list[list[Region]] = []
        self.plates: list[Plate] = []

        for y in range(self.height):
            self.regions.append(self._create_regions(y, y + 1))

    def _create_regions(self, top_y: int, bottom_y: int) -> list[Region]:
        """Creates a list of regions. These span all longitude values.
        Latitude values are decided by top_y, bottom_y, and the height setting"""
        circle = []
        top_radians = (self.height / 2 - top_y) * math.pi / self.height
        bottom_radians = (self.height / 2 - bottom_y) * math.pi / self.height

        sine_diff_r = (math.sin(top_radians) -
                       math.sin(bottom_radians)) * self.radius
        area = int(sine_diff_r * self.circumference)

        top_width = int(math.cos(top_radians) * self.radius /
                        self.length * 2 * math.pi)
        bottom_width = int(math.cos(bottom_radians) *
                           self.radius / self.length * 2 * math.pi)
        # Cost influences how quickly an area can expand, by setting a price for expansion to a region
        # This value should be standardized for all choices of length and area
        # I haven't done the calculations, but this seems to standardize to a maximum of 1.00
        cost = round(area * self.length / self.circumference**2, 2)

        for x in range(self.length):
            circle.append(Region(x, top_y, top_width,
                          bottom_width, self.region_height, area, cost))

        return circle

    def get_region(self, x: int, y: int) -> Region:
        """Returns the region at (x,y)"""
        return self.regions[y][x]

    def get_subregion(self, x: int, y: int) -> Subregion:
        """Returns the subregion at (x,y)"""
        region = self.get_region(x/5, y/5)
        subregion = region.get_subregion(x % 5, y % 5)
        return subregion

    def create_plates(self, land_amount: int, water_amount: int) -> None:
        """Creates the starting points of tectonic plates at random coordinates"""
        for id in range(land_amount + water_amount):
            if id >= land_amount:
                type = constants.WATER
            else:
                type = random.randrange(9)

            while True:
                x = random.randrange(self.length)
                y = random.randrange(self.height)
                if self.regions[y][x].plate == -1:
                    break
            self.plates.append(Plate(id, self.regions, x, y, type))

    def expand_plates(self) -> bool:
        """Expands all tectonic plates once. Level of expansion is determined by plate growth settings"""
        finished = True

        for plate in self.plates:
            if plate.alive:
                finished = False
            else:
                continue

            plate.restore()
            currency = plate.expand()
            while currency > 0:
                currency = plate.expand()
        return finished

    def build_plates(self):
        """Expands all tectonic plates until the entire world is covered"""
        while True:
            finished = self.expand_plates()
            if finished:
                break

    def create_continents(self):
        """Creates land and water on all plates"""
        for plate in self.plates:
            plate.create_land()

    def find_outlines(self):
        for circle in self.regions:
            for region in circle:
                x = region.x
                y = region.y

                if x + 1 < self.length:
                    if region.plate != self.regions[y][x + 1].plate:
                        region.east_outline = True
                if y + 1 < self.height:
                    if region.plate != self.regions[y + 1][x].plate:
                        region.south_outline = True

    def get_plate(self, x: int, y: int) -> Plate:
        """Returns the plate occupying the region at (x,y)"""
        id = self.get_region(x, y).plate
        return self.plates[id]
