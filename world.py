from region import Region
from plate import Plate
from region_metrics import RegionMetrics
from boundary import Boundary
from line_generator import LineGenerator
from typing import Any
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
        self.region_size = 360 // length

        self.regions: list[list[Region]] = []
        self.subregions: list[list[Region]] = []
        self.plates: list[Plate] = []

        self.km_squares_dicts: dict[str, list[int]] = None

        self.fixed_growth = True

        self.boundary: Boundary = None

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
        cost = round(area * length**2 / self.circumference**2, 4)
        # I want to see 4 decimals. Still not higher than 1? Change back to 2 later

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

    def get_next_region(self, x: int, y: int, dir: int) -> Region:
        """Returns a region adjacent to (x,y)"""
        nx, ny = constants.get_next_index(x, y, dir, self.length, self.height)
        return self.regions[ny][nx]

    def get_subregion(self, x: int, y: int) -> Region:
        """Returns the subregion at (x,y)"""
        return self.subregions[y][x]

    def get_subregion_of_region(self, x: int, y: int, region_x: int, region_y: int) -> Region:
        """Returns the subregion at (x, y) within region at (region_x, region_y)"""
        return self.subregions[region_y * self.region_size + y][region_x * self.region_size + x]

    def get_all_subregions(self, positions: list[tuple[int]]) -> list[Region]:
        """Returns a list of subregions corresponding to a list of coordinates"""
        result = []

        for x, y in positions:
            try:
                result.append(self.subregions[y][x])
            except IndexError:
                result.append(None)

        return result

    def get_subregions_by_terrain(self) -> dict[list[Region]]:
        """Returns all subregions divided by terrain"""
        result = {}

        for row in self.subregions:
            for subregion in row:
                if subregion.terrain in result:
                    result[subregion.terrain].append(subregion)
                else:
                    result[subregion.terrain] = [subregion]
        return result

    def create_plates(self, land_amount: int, water_amount: int, odd_amount: int,
                      margin: float, island_rate: float,
                      min_growth: int, max_growth: int, odd_growth: int,
                      world_map: list[list[Region]], fixed_growth: bool) -> None:
        """Creates the starting points of tectonic plates at random coordinates"""
        self.fixed_growth = fixed_growth

        for id in range(land_amount + water_amount + odd_amount):
            if id >= odd_amount + land_amount:
                type = constants.WATER
                growth = random.randrange(min_growth, max_growth + 1)
                relative_growth = 0.3
            elif id >= odd_amount:
                type = random.randrange(9)
                growth = random.randrange(min_growth, max_growth + 1)
                relative_growth = 0.3
            else:
                type = constants.CENTER
                growth = odd_growth
                relative_growth = 0.6

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
                                     type=type, margin=margin, island_rate=island_rate, growth=growth,
                                     relative_growth=relative_growth))

    def expand_plates(self) -> bool:
        """Expands all tectonic plates once. Level of expansion is determined by plate growth settings.
        Returns true when tectonic plates cover the entire world"""
        finished = True

        for plate in self.plates:
            if plate.alive:
                finished = False
            else:
                continue

            if self.fixed_growth:
                plate.expand()
            else:
                plate.expand_blindly()

        return finished

    def build_plates(self) -> None:
        """Expands all tectonic plates until the entire world is covered"""
        while True:
            finished = self.expand_plates()
            if finished:
                break

    def create_continents(self) -> None:
        """Creates land and water on all plates"""
        for plate in self.plates:
            plate.create_land()

    def find_maximum_key(self, dictionary: dict[Any, int]) -> Any:
        """Returns the key which holds the dictionarys max value"""
        max_key = None
        max_value = None

        for key, value in dictionary.items():
            if max_value is None or value > max_value:
                max_key = key
                max_value = value
        return max_key

    def find_region_main_terrain(self, region: Region) -> int:
        """Returns the most common terrain within the subregions of a region"""
        region_x = region.x
        region_y = region.metrics.y
        terrain_count = dict()

        for sub_x in range(self.region_size):
            for sub_y in range(self.region_size):
                subregion = self.get_subregion_of_region(
                    sub_x, sub_y, region_x, region_y)

                if subregion.terrain in terrain_count:
                    terrain_count[subregion.terrain] += 1
                else:
                    terrain_count[subregion.terrain] = 1

        return self.find_maximum_key(terrain_count)

    def update_regions_from_subregions(self) -> None:
        """Sets region variables based on subregion variables"""
        for y in range(self.height):
            for x in range(self.length):
                region = self.get_region(x, y)
                region.set_terrain(self.find_region_main_terrain(
                    region), set_update_flag=False)

    def update_subregions_from_regions(self) -> None:
        """Sets subregion variables based on region variables"""
        for y in range(self.sub_height):
            for x in range(self.sub_length):
                ry = y // self.region_size
                region = self.get_region(x // self.region_size, ry)
                subregion = self.get_subregion(x, y)
                subregion.set_terrain(region.terrain)

                if subregion.plate == -1:
                    subregion.plate = region.plate

    def update_kilometers_from_subregion(self, subregion: Region, km_map: dict[str, list[int]]) -> None:
        """Updates the terrain of all square kilometers in a subregion"""
        for index in range(len(km_map["x"])):
            if km_map["subregion_x"][index] == subregion.x \
                    and km_map["subregion_y"][index] == subregion.metrics.y:
                km_map["terrain"][index] = subregion.terrain

    def update_kilometers_from_region(self, active_region: Region,
                                      km_map: dict[str, list[int]]) -> None:
        """Updates the terrain of all square kilometers in a region"""
        for y in range(self.region_size):
            for x in range(self.region_size):
                subregion = self.get_subregion_of_region(
                    x, y, active_region.x, active_region.metrics.y)

                if subregion.update_subdivision:
                    self.update_kilometers_from_subregion(subregion, km_map)
                    subregion.update_subdivision = False

    def find_plate_boundaries(self):
        """Finds plate boundaries on a subregion level"""
        for y in range(self.sub_height - 1):
            for x in range(self.sub_length):
                nx = (x + 1) % self.sub_length
                ny = y + 1
                region = self.subregions[y][x]
                east = self.subregions[y][nx]
                south = self.subregions[ny][x]

                if region.plate != east.plate:
                    region.east_boundary = True
                    east.west_boundary = True

                if region.plate != south.plate:
                    region.south_boundary = True
                    south.north_boundary = True

    def get_plate(self, plate_id: int) -> Plate:
        """Returns the plate with the given id

        Raises:
            IndexError"""
        try:
            return self.plates[plate_id]
        except IndexError:
            raise IndexError(
                f"Attempt to access nonexistant tectonic plate {plate_id}")

    def get_land_area(self) -> int:
        """Calculates total land area"""
        area = 0
        for circle in self.regions:
            for region in circle:
                if constants.is_type(region.terrain, constants.LAND):
                    area += region.metrics.area
        return area

    def get_sea_area(self) -> int:
        """Calculates total sea area"""
        area = 0
        for circle in self.regions:
            for region in circle:
                if constants.is_type(region.terrain, constants.WATER):
                    area += region.metrics.area
        return area

    def _find_coastline_exit(self, entrance: int, northeast: int, southeast: int,
                             southwest: int, northwest: int,
                             enclosed_terrain: int = constants.LAND) -> int:
        """Finds the direction of the coastline exit,
        given the terrain of four cells in a square.
        Assumes clockwise travel around a land mass.
        In the case that two land masses meet on a diagonal,
        the coastline exit of the current landmass is returned."""

        # I used to do something like northeast == LAND and northwest == WATER
        # which was easier to read. But it wouldn't let me find something like
        # lake shores, forest edges or coastline edges
        # where there are some mountains by the shore
        if constants.is_type(northeast, enclosed_terrain) and \
                constants.is_type(northwest, enclosed_terrain) == False:
            if constants.is_type(southwest, enclosed_terrain) \
                    and constants.is_type(southeast, enclosed_terrain) == False:
                # Rare case of diagonal land masses. Either go EAST to NORTH or WEST to SOUTH
                return constants.angle_direction(entrance, 6)
            else:
                return constants.NORTH
        elif constants.is_type(southeast, enclosed_terrain) and \
                constants.is_type(northeast, enclosed_terrain) == False:
            if constants.is_type(northwest, enclosed_terrain) and \
                    constants.is_type(southwest, enclosed_terrain) == False:
                return constants.turn_direction(entrance, 6)
            else:
                return constants.EAST
        elif constants.is_type(southwest, enclosed_terrain) and \
                constants.is_type(southeast, enclosed_terrain) == False:
            return constants.SOUTH
        elif constants.is_type(northwest, enclosed_terrain) and \
                constants.is_type(southwest, enclosed_terrain) == False:
            return constants.WEST

    def _find_coastline_entrance(self, exit: int, northeast: int, southeast: int,
                                 southwest: int, northwest: int,
                                 enclosed_terrain: int = constants.LAND) -> int:
        """Finds the direction of the coastline entrance,
        given the terrain of four cells in a square.
        Assumes clockwise travel around a land mass.
        In the case that two land masses meet on a diagonal,
        the coastline entrance of the current landmass is returned."""

        if constants.is_type(northeast, enclosed_terrain) and \
                constants.is_type(southeast, enclosed_terrain) == False:
            if constants.is_type(southwest, enclosed_terrain) and \
                    constants.is_type(northwest, enclosed_terrain) == False:
                # Rare case of diagonal land masses. Either go EAST to NORTH or WEST to SOUTH
                return constants.angle_direction(exit, 2)
            else:
                return constants.EAST
        elif constants.is_type(southeast, enclosed_terrain) and \
                constants.is_type(southwest, enclosed_terrain) == False:
            if constants.is_type(northwest, enclosed_terrain) and \
                    constants.is_type(northeast, enclosed_terrain) == False:
                return constants.angle_direction(exit, 2)
            else:
                return constants.SOUTH
        elif constants.is_type(southwest, enclosed_terrain) and \
                constants.is_type(northwest, enclosed_terrain) == False:
            return constants.WEST
        elif constants.is_type(northwest, enclosed_terrain) and \
                constants.is_type(northeast, enclosed_terrain) == False:
            return constants.NORTH

    def _find_square_regions(self, x: int, y: int, dir: int) -> tuple[Region]:
        """Returns a tuple of regions in order (NORTHEAST, SOUTHEAST, SOUTHWEST, NORTHWEST)
        given the coordinates and relative placement of one of these regions"""
        result = [None, None, None, None]

        if dir == constants.NORTHEAST:
            result[0] = self.get_region(x, y)
            result[1] = self.get_next_region(x, y, constants.SOUTH)
            result[2] = self.get_next_region(x, y, constants.SOUTHWEST)
            result[3] = self.get_next_region(x, y, constants.WEST)
        elif dir == constants.SOUTHEAST:
            result[0] = self.get_next_region(x, y, constants.NORTH)
            result[1] = self.get_region(x, y)
            result[2] = self.get_next_region(x, y, constants.WEST)
            result[3] = self.get_next_region(x, y, constants.NORTHWEST)
        elif dir == constants.SOUTHWEST:
            result[0] = self.get_next_region(x, y, constants.NORTHEAST)
            result[1] = self.get_next_region(x, y, constants.EAST)
            result[2] = self.get_region(x, y)
            result[3] = self.get_next_region(x, y, constants.NORTH)
        elif dir == constants.NORTHWEST:
            result[0] = self.get_next_region(x, y, constants.EAST)
            result[1] = self.get_next_region(x, y, constants.SOUTHEAST)
            result[2] = self.get_next_region(x, y, constants.SOUTH)
            result[3] = self.get_region(x, y)
        return result

    def _find_region_in_direction(self, x: int, y: int, dir: int,
                                  terrain: int, limit: int = 60) -> Region:
        """Finds the first region with the given terrain,
        starting at (x,y) and moving in the given direction.
        A search limit can be provided.
        If the search succeeds, returns the
        the last region not to have the given terrain.
        If the search fails, returns None."""

        region = self.get_region(x, y)

        if region.terrain == terrain:
            return None

        while limit > 0:
            x, y = constants.get_next_coordinates(x, y, dir)
            previous_region = region
            limit -= 1

            if constants.within_bounds(x, y, self.length, self.height):
                region = self.get_region(x, y)
                if region.terrain == constants.WATER:
                    return previous_region
            else:
                break

    def find_region_coastline(self, x: int, y: int) -> list[Region]:
        """Generate a random coastline for the given a land region.
        Returns a list of coastline regions.
        If the coordinates points to an ocean region, returns None"""

        # TODO fix errors at the poles. Try ending the coastline
        # Then, go back to the starting point, change to counter-clockwise and generate
        # Some functions assume clockwise direction

        coastline = []

        # If the user selected a landmass in the middle of a continent, I search outwards
        # Search north first. Algorithm will be less than efficient if coastline
        # is nearby but not to the north
        # TODO but that's no good. The user should click on the actual coastline
        # or on a region one cell away from it
        for dir in range(1, 8, 2):
            region = self._find_region_in_direction(
                x, y, dir, constants.WATER)

            if region is not None:
                coastline.append(region)
                # This will find ne, se, sw, nw regions surrounding a relevant coastline
                surroundings = self._find_square_regions(region.x, region.metrics.y,
                                                         constants.angle_direction(dir, 5))

                entrance = constants.angle_direction(dir, 6)
                exit = self._find_coastline_exit(entrance, *surroundings)
                start_x = region.x
                start_y = region.metrics.y
                start_entrance = entrance

                # The boundary is as large as a region,
                # located in the middle of the surroundings
                # Use the northwest region to calculate starting coordinates
                boundary_x = surroundings[3].x * \
                    self.region_size + self.region_size // 2
                boundary_y = surroundings[3].metrics.y * \
                    self.region_size + self.region_size // 2

                self.boundary = Boundary(entrance=entrance,
                                         exit=exit,
                                         length=self.region_size,
                                         height=self.region_size,
                                         start_x=boundary_x,
                                         start_y=boundary_y,
                                         line_terrain=constants.LAND,
                                         primary_terrain=constants.LAND,
                                         secondary_terrain=constants.WATER)
                break
        if region is None:
            return None

        while True:
            entrance = constants.flip_direction(exit)
            # Find next entrance region from coastline and exit direction
            # The coastline is searched in a clockwise direction,
            # meaning I can always get the correct entrance region from the exit direction
            if exit == constants.NORTH:
                # So previous exit NORTH means exit region is NORTHEAST
                # NORTHEAST has index 0 in surroundings
                # Flip exit region to get entrance region SOUTHEAST
                region = surroundings[0]
                surroundings = self._find_square_regions(
                    region.x, region.metrics.y, constants.SOUTHEAST)
            elif exit == constants.EAST:
                region = surroundings[1]
                surroundings = self._find_square_regions(
                    region.x, region.metrics.y, constants.SOUTHWEST)
            elif exit == constants.SOUTH:
                region = surroundings[2]
                surroundings = self._find_square_regions(
                    region.x, region.metrics.y, constants.NORTHWEST)
            elif exit == constants.WEST:
                region = surroundings[3]
                surroundings = self._find_square_regions(
                    region.x, region.metrics.y, constants.NORTHEAST)

            if region.x == start_x and region.metrics.y == start_y and entrance == start_entrance:
                return coastline
            else:
                exit = self._find_coastline_exit(entrance, *surroundings)

                coastline.append(region)
                self.boundary.add_segment(exit)

    def apply_line_on_region(self, line: LineGenerator):
        """Generates terrain using a line generator"""
        start_x, start_y = line.get_grid_offset()

        for x in range(line.length):
            for y in range(line.height):
                subregion = self.get_subregion(
                    (start_x + x) % self.length, start_y + y)
                terrain = line.get_terrain(x, y)

                if not constants.is_type(subregion.terrain, terrain):
                    subregion.set_terrain(terrain)

    def generate_region_coastline(self):
        """Generates terrain using the saved boundary"""
        if self.boundary is not None:
            self.boundary.generate()

        for line in self.boundary.get_path():
            self.apply_line_on_region(line)

    def construct_region(self, region_x: int, region_y: int) -> dict[str, list[int]]:
        """Constructs the region at (x, y) down to kilometer-level precision"""

        vertical = self.subregions[0][0].metrics.vertical_stretch
        # If I have regions in this format, it'll be hard to navigate in compass directions
        # I could try something like
        # data = {(x, y): {terrain: int, subregion_x: int, subregion_y: int, subregion_border: int}}
        # I don't need to use a two-dimensional list, this should be faster
        # More importantly, it allows for negative indexes
        data = {"x": [], "y": [], "terrain": [],
                "subregion_x": [], "subregion_y": [],
                "subregion_border": []}
        line = []

        for sub_y in range(self.region_size):
            subregion = self.get_subregion_of_region(
                0, sub_y, region_x, region_y)
            top = subregion.metrics.top_stretch
            bottom = subregion.metrics.bottom_stretch

            for step in range(vertical):
                horizontal = round(top + (bottom - top) * step / vertical)
                line.append(horizontal)

        for kilometer_y, stretch in enumerate(line):
            for x in range(stretch * self.region_size):
                subregion_x = x // stretch
                subregion_y = kilometer_y // vertical
                subregion = self.get_subregion_of_region(
                    subregion_x, subregion_y, region_x, region_y)

                kilometer_x = x - stretch * self.region_size // 2

                # entry = dict()
                # Add some stuff...
                # data[(kilometer_x, kilometer_y)] = entry

                data["x"].append(kilometer_x - stretch *
                                 (self.region_size // 2))
                data["y"].append(kilometer_y)
                data["subregion_x"].append(subregion_x)
                data["subregion_y"].append(subregion_y)
                data["terrain"].append(subregion.terrain)

                if kilometer_x % stretch == 0 or kilometer_y % vertical == 0:
                    data["subregion_border"].append(1)
                else:
                    data["subregion_border"].append(0)

        self.km_squares_dicts = data
        return self.km_squares_dicts
