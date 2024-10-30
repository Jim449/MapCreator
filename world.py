from region import Region
from plate import Plate
from region_metrics import RegionMetrics
import constants
import math
import random


class World():
    """Represents the world"""

    def __init__(self, radius: int = 6372, length: int = 72, height: int = 36,
                 sub_length=360, sub_height=180):
        """Creates a new world, separated into regions.
        Length/height specify how many regions fit horizontally and vertically.
        Length should be twice the value of height in order to mimic longitude and latitude"""
        super().__init__()

        self.radius: int = radius
        self.circumference: int = int(2 * radius * math.pi)
        self.area: int = int(4 * math.pow(radius, 2) * math.pi)
        self.region_height: int = int(self.circumference / length)
        self.subregion_height: int = int(self.circumference / sub_length)

        self.length = length
        self.height = height
        self.sub_length = sub_length
        self.sub_height = sub_height

        self.regions: list[list[Region]] = []
        self.subregions: list[list[Region]] = []
        self.plates: list[Plate] = []

        for y in range(height):
            metrics = self._get_region_metric(
                y, length, height, self.region_height)
            self.regions.append(self._create_regions(length, metrics))

        for y in range(self.sub_height):
            metrics = self._get_region_metric(
                y, sub_length, sub_height, self.subregion_height)
            self.subregions.append(self._create_regions(sub_length, metrics))

    def _get_region_metric(self, y: int, length: int, height: int,
                           vertical_stretch: int) -> RegionMetrics:
        """Returns shared region metrics for all regions on same latitude"""
        top_radians = (height / 2 - y) * math.pi / height
        bottom_radians = (height / 2 - (y + 1)) * math.pi / height

        sine_diff_r = (math.sin(top_radians) -
                       math.sin(bottom_radians)) * self.radius
        area = int(sine_diff_r * self.circumference / length)

        top_width = int(math.cos(top_radians) * self.radius /
                        length * 2 * math.pi)
        bottom_width = int(math.cos(bottom_radians) *
                           self.radius / length * 2 * math.pi)

        # Cost influences how quickly an area can expand, by setting a price for expansion to a region
        # This value should be standardized for all choices of length and area
        # I haven't done the calculations, but this seems to standardize to a maximum of 1.00
        cost = round(area * length**2 / self.circumference**2, 2)

        return RegionMetrics(area=area, top_stretch=top_width, bottom_stretch=bottom_width,
                             vertical_stretch=vertical_stretch, cost=cost, y=y,
                             length_division=length)

    def _create_regions(self, length: int, metrics: RegionMetrics) -> list[Region]:
        """Creates a list of regions on the same latitude. These span all longitude values"""
        circle = []
        for x in range(length):
            circle.append(Region(x, metrics))
        return circle

    def get_region(self, x: int, y: int) -> Region:
        """Returns the region at (x,y)"""
        return self.regions[y][x]

    def get_subregion(self, x: int, y: int) -> Region:
        """Returns the subregion at (x,y)"""
        return self.subregions[y][x]

    def get_subregion_of_region(self, x: int, y: int, region_x: int, region_y: int) -> Region:
        """Returns the subregion at (x, y) within region at (region_x, region_y)"""
        return self.subregion[region_y * 5 + y][region_x * 5 + x]

    def create_plates(self, land_amount: int, water_amount: int, odd_amount: int,
                      margin: float, island_rate: float,
                      min_growth: int, max_growth: int, odd_growth: int,
                      world_map: list[list[Region]]) -> None:
        """Creates the starting points of tectonic plates at random coordinates"""
        for id in range(land_amount + water_amount + odd_amount):
            if id >= odd_amount + land_amount:
                type = constants.WATER
                growth = random.randrange(min_growth, max_growth + 1)
            elif id >= odd_amount:
                type = random.randrange(9)
                growth = random.randrange(min_growth, max_growth + 1)
            else:
                type = constants.CENTER
                growth = odd_growth

            if id < odd_amount:
                x = len(world_map[0]) // 2
                y = len(world_map) // 2
            else:
                while True:
                    x = random.randrange(len(world_map[0]))
                    y = random.randrange(len(world_map))
                    if world_map[y][x].plate == -1:
                        break

            self.plates.append(Plate(id=id, world_map=world_map, start_x=x, start_y=y,
                                     type=type, margin=margin, island_rate=island_rate, growth=growth))

    def expand_plates(self) -> bool:
        """Expands all tectonic plates once. Level of expansion is determined by plate growth settings.
        Returns true when tectonic plates cover the entire world"""
        finished = True

        for plate in self.plates:
            if plate.alive:
                finished = False
            else:
                continue

            plate.restore()
            plate.expand()
            # My algorith doesn't work too well for subregions when growth is high
            # It creates predictable rhomb-shaped areas
            # I tend to get this race to capture the last free spots
            # That may lead to multi-area intersections which I don't want

            # First, multiplying subregion growth with 25 is over the top
            # I could use a maximum selectable growth of 10
            # For subregions, that can be multiplied by 2, so I get 20

            # While that's better, I've underestimated just how large these areas are
            # A growth multiplier of 5 should be fine
            # I still have an expansion race problem
            # Increasing growth might actually remedy it, by giving maximum growth
            # to plates which have slightly more spaces to grow, allowing them to block faster
            # So 4x5=20 growth is fine...
            # Try with 10x5=50 growth and see if it's acceptable
            # No, that is not acceptable
            # Try with 8x5 = 40 growth
            # No, that is not acceptable
            # Try with 6x5 = 30 growth
            # That's not really acceptable either
            # Try with 5x5 = 25 growth
            # It's still not that great
            # A multipler of 5 is probably no good after all

            # Go ahead and test growths for low-resolution plates
            # Start with 4
            # Sure
            # How about 10?
            # No way!
            # Maybe 8?
            # Decent enough. Maybe not
            # Perhaps 6?
            # Fine

            # I could go with a maximum of 8, multiplier of 4 giving 32
            # I'll have standards of 4 and 16
            # But a maximum of 32 is a bit much

            # Let's experiment with larger variance. 1-8 sizes!

            # Let's add a supercontinent!
            # I need another spinbox for that one

            # I've seen strange continent behaviour at the pole
            # I need to ensure x, y sea margins are really set to 0
            # That shouldn't be an issue
            # I need to ensure west, east span the entire globe where they're supposed to
            # I'm not sure what's happening there. I need some debugging

            # I should improve performance
            # Regions which cannot be expanded from should be moved to another list
            # Then I'll have less elements to sort and iterate over
            # DONE!

            # Note that the number of border cells on an area tend to grow like
            # 1, 4, 8, 12, 16... or +4 per iteration
            # It's a slow growth, total size grows much faster
            # 2x border cells roughly corresponds to 3-4x area

            # One option is to remove the while loop
            # (currency = plate.expand() while currency > 0: plate.expand())
            # If there is an excess currency, it'll have to be used up
            # on the next expand_plate-call
            # This will limit rapid growth of areas with little place to expand
            # While-loop removed!
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

    def get_plate(self, x: int, y: int, precision: str = "Region") -> Plate:
        """Returns the plate occupying the region at (x,y)

        Raises:
            IndexError"""
        if precision == "Subregion":
            id = self.get_subregion(x, y).plate
        else:
            id = self.get_region(x, y).plate

        try:
            return self.plates[id]
        except IndexError:
            raise IndexError(
                f"Attempt to access nonexistant tectonic plate in region ({x}, {y})")

    def get_land_area(self) -> int:
        """Calculates total land area"""
        area = 0
        for circle in self.regions:
            for region in circle:
                if region.terrain in (constants.LAND, constants.MOUNTAIN):
                    area += region.metrics.area
        return area

    def get_sea_area(self) -> int:
        """Calculates total sea area"""
        area = 0
        for circle in self.regions:
            for region in circle:
                if region.terrain in (constants.WATER, constants.SHALLOWS, constants.SHALLOWS_2):
                    area += region.metrics.area
        return area
