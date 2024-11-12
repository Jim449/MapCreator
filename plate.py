from region import Region
import random
import math
import constants


class Plate():
    def __init__(self, id: int, world_map: list[list[Region]], start_x: int, start_y: int,
                 type: int = constants.CENTER, margin: float = 0.25, island_rate: float = 0.1,
                 growth: int = 4, relative_growth: float = 0.3):
        self.id: int = id
        self.world_map: list[list[Region]] = world_map
        self.start_x: int = start_x
        self.start_y: int = start_y
        self.max_x = len(world_map[0])
        self.max_y = len(world_map)
        self.type: int = type
        self.margin: float = margin
        self.island_rate: float = island_rate
        self.growth: int = growth
        self.relative_growth = relative_growth

        self.currency: float = growth
        self.alive: bool = True
        self.area: int = 0
        self.land_area: int = 0
        self.sea_area: int = 0
        self.pole_type: int = 0
        self.claimed_regions: list[Region] = []
        self.queued_regions: list[Region] = []

        # This keeps track of the plates boundaries
        # For a vertical line at y, store minimum and maximum x values
        # Assume the plate starts at x = 71 where 71 is the far east
        # Then west_end = east_end = 71
        # Assume the plate expands east
        # Then west_end = 71 and east_end = 72
        # Horizontal stretch at y can then be easily calculated as 72-71+1 = 2
        # Therefore, 72 is the correct coordinate to use in east_end and it points to index 0
        self.west_end: dict[int, int] = {start_y: start_x}
        self.east_end: dict[int, int] = {start_y: start_x}
        self.north_end: dict[int, int] = {start_x: start_y}
        self.south_end: dict[int, int] = {start_x: start_y}

        self.horizontal_distance: dict[int, int] = {}
        self.vertical_distance: dict[int, int] = {}
        self.ascending_distance: dict[int, int] = {}
        self.descending_distance: dict[int, int] = {}

        if start_y == 0 or start_y == self.max_y - 1:
            self.claim_pole(start_y)
        else:
            self.claim_region(start_x, start_y)

    def _get_coordinates(self, x: int, y: int) -> tuple[int]:
        """Translates coordinates (x,y) into valid indexes,
        usable to access a region from the region list.
        Any index coordinate (x,y) is valid,
        with out of bounds values treated as circling around the globe"""
        if y < 0:
            new_y = - 1 - y
            x += self.max_x // 2
        elif y >= self.max_y:
            new_y = 2*self.max_y - y - 1
            x += self.max_x // 2
        else:
            new_y = y
        new_x = x % self.max_x
        return (new_x, new_y)

    def _get_next_coordinates(self, x: int, y: int, dir: int) -> tuple[int]:
        """Returns new coordinates (x,y) after travelling once in a direction.
        Give direction NORTH, EAST, SOUTH or WEST from constants"""
        if dir == constants.NORTH:
            return (x, y-1)
        elif dir == constants.EAST:
            return (x+1, y)
        elif dir == constants.SOUTH:
            return (x, y+1)
        elif dir == constants.WEST:
            return (x-1, y)
        else:
            return (x, y)

    def _get_circular_coordinate(self, value: int, max_value: int, horizontal: bool,
                                 end_of_region: bool = False) -> int:
        """Gets longitude or latitude coordinates"""
        if value < 0:
            value += max_value
        elif value >= max_value:
            value -= max_value

        if horizontal and end_of_region:
            step = 360 // max_value
            return (value + 1) * step - 180
        elif horizontal:
            step = 360 // max_value
            return value * step - 180
        elif end_of_region:
            step = 180 // max_value
            return (0 - value - 1) * step + 90
        else:
            step = 180 // max_value
            return (0 - value) * step + 90

    def _set_boundary(self, minimum: dict[int, int], maximum: dict[int, int],
                      key: int, value: int) -> None:
        """Updates boundaries

        Arguments:
            self.west_end, self.east_end, y, x
        Or:
            self.north_end, self.south_end, x, y"""
        if key in minimum:
            if value < minimum[key]:
                minimum[key] = value
            elif value > maximum[key]:
                maximum[key] = value
        else:
            minimum[key] = value
            maximum[key] = value

    def _add_or_set(self, dictionary: dict[int, int], key: int):
        """Adds value by 1 if key exists, otherwise, sets value to 1"""
        if key in dictionary:
            dictionary[key] += 1
        else:
            dictionary[key] = 1

    def _add_distance(self, x: int, y: int) -> None:
        """Increases appropriate horizontal and vertical distances by 1,
        based on claiming the region at (x, y)"""
        # Find the x-value when y = 0 and use that as key for diagonal distance
        asc_key = (x - y) % self.max_x
        des_key = (x + y) % self.max_x

        self._add_or_set(self.ascending_distance, asc_key)
        self._add_or_set(self.descending_distance, des_key)
        self._add_or_set(self.horizontal_distance, y)
        self._add_or_set(self.vertical_distance, x)

    def claim_region(self, x: int, y: int) -> None:
        """Claims a region. Updates plate boundaries and pays region cost"""
        ix, iy = self._get_coordinates(x, y)
        region = self.world_map[iy][ix]
        region.plate = self.id
        region.plate_x = x
        region.plate_y = y
        region.active = False
        self.area += region.metrics.area
        self.currency -= region.metrics.cost
        self.queued_regions.append(region)
        self._set_boundary(self.west_end, self.east_end, iy, x)
        self._set_boundary(self.north_end, self.south_end, ix, y)
        self._add_distance(ix, iy)

    def claim_pole(self, y: int) -> None:
        """Claims an entire horizontal circle at a pole.
        Updates plate boundaries and pays region costs"""
        for x in range(self.max_x):
            self.claim_region(x, y)

        self.relative_growth = 0.05

        # Have land centering at the pole
        if y == 0 and self.type != constants.WATER:
            self.type = constants.NORTH
            self.pole_type = constants.NORTH
        elif y == self.max_y - 1 and self.type != constants.WATER:
            self.type = constants.SOUTH
            self.pole_type = constants.SOUTH

    def _awaken_regions(self) -> int:
        """Counts amount of regions which the plate can expand from"""
        amount = 0
        for region in self.queued_regions:
            region.active = True
            amount += 1
        return amount

    def expand(self) -> int:
        """Expands the plate in random directions. Returns remaining growth currency.
        Plates will expand no faster than 1 cell per method call in any direction.
        Plates will expand efficiently into vacant spaces.
        If a plate has little space to expand, it will expand with greater focus
        to claim the vacant spaces.
        """
        active_regions = self._awaken_regions()
        limit = math.ceil(active_regions * 0.75)
        self.currency += self.growth

        if active_regions == 0:
            self.alive = False
            return 0

        random.shuffle(self.queued_regions)

        while limit > 0 and self.currency > 0:
            region = self.queued_regions[0]
            if not region.active:
                break

            for dir in range(1, 8, 2):
                x, y = self._get_next_coordinates(
                    region.plate_x, region.plate_y, dir)
                ix, iy = self._get_coordinates(x, y)

                if self.world_map[iy][ix].plate == -1:
                    if iy == 0 or iy == self.max_y - 1:
                        self.claim_pole(y)
                    else:
                        self.claim_region(x, y)
            region.active = False
            limit -= 1
            self.claimed_regions.append(region)
            self.queued_regions.remove(region)
        return self.currency

    def expand_blindly(self) -> int:
        """Expands the plate in random directions. Returns remaining growth currency.
        Plates will expand no faster than 1 cell per method call in any direction.
        Plates expansion should not speed up even if expansion choices are limited"""
        active_regions = self._awaken_regions()
        limit = math.ceil(active_regions * 0.75)
        self.currency += active_regions * self.relative_growth

        if active_regions == 0:
            self.alive = False
            return 0

        random.shuffle(self.queued_regions)

        while limit > 0 and self.currency > 0:
            region = self.queued_regions[0]
            if not region.active:
                break

            for dir in range(1, 8, 2):
                x, y = self._get_next_coordinates(
                    region.plate_x, region.plate_y, dir)
                ix, iy = self._get_coordinates(x, y)

                if self.world_map[iy][ix].plate == -1:
                    if iy == 0 or iy == self.max_y - 1:
                        self.claim_pole(y)
                    else:
                        self.claim_region(x, y)
            region.active = False
            self.claimed_regions.append(region)
            self.queued_regions.remove(region)
            limit -= 1
        return self.currency

    def _horizontal_land_scan(self) -> None:
        """Scans plate horizontally, finding valid land positions on each vertical"""
        if self.type in (constants.WEST, constants.CENTER, constants.EAST):
            north_margin = self.margin
            south_margin = self.margin
        elif self.type in (constants.NORTHWEST, constants.NORTH, constants.NORTHEAST):
            north_margin = 0
            south_margin = self.margin * 2
        elif self.type in (constants.SOUTHWEST, constants.SOUTH, constants.SOUTHEAST):
            north_margin = self.margin * 2
            south_margin = 0

        for column in self.north_end.keys():
            length = self.vertical_distance[column]
            start = self.north_end[column]
            end = self.south_end[column]

            first_skip = int(length * north_margin)
            second_skip = int(length * south_margin)
            include = length - first_skip - second_skip

            for row in range(start, end + 1):
                x, y = self._get_coordinates(column, row)
                if self.world_map[y][x].plate == self.id:
                    if first_skip > 0:
                        first_skip -= 1
                    elif include > 0:
                        self.world_map[y][x].horizontal_land_check = True
                        include -= 1
                    else:
                        break

    def _vertical_land_scan(self) -> None:
        """Scans plate vertically, finding valid land positions on each horizontal"""

        if self.pole_type in (constants.NORTH, constants.SOUTH):
            # Poles will cover entire horizontal in places, margins would look odd
            west_margin = 0
            east_margin = 0
        elif self.type in (constants.NORTH, constants.CENTER, constants.SOUTH):
            west_margin = self.margin
            east_margin = self.margin
        elif self.type in (constants.NORTHWEST, constants.WEST, constants.SOUTHWEST):
            west_margin = 0
            east_margin = self.margin * 2
        elif self.type in (constants.NORTHEAST, constants.EAST, constants.SOUTHEAST):
            west_margin = self.margin * 2
            east_margin = 0

        for row in self.west_end.keys():
            length = self.horizontal_distance[row]
            start = self.west_end[row]
            end = self.east_end[row]

            first_skip = int(length * west_margin)
            second_skip = int(length * east_margin)
            include = length - first_skip - second_skip

            for column in range(start, end + 1):
                x, y = self._get_coordinates(column, row)
                if self.world_map[y][x].plate == self.id:
                    if first_skip > 0:
                        first_skip -= 1
                    elif include > 0:
                        self.world_map[y][x].vertical_land_check = True
                        include -= 1
                    else:
                        break

    def _ascending_land_scan(self) -> None:
        """Scans the plate diagonally, finding valid land position in northwest to southeast diagonal"""
        if self.type in (constants.NORTH, constants.WEST, constants.NORTHWEST):
            northwest_margin = 0
            southeast_margin = self.margin * 2
        elif self.type in (constants.CENTER, constants.NORTHEAST, constants.SOUTHWEST):
            northwest_margin = self.margin
            southeast_margin = self.margin
        elif self.type in (constants.EAST, constants.SOUTHEAST, constants.SOUTH):
            northwest_margin = self.margin * 2
            southeast_margin = 0

        for start_x, length in self.ascending_distance.items():
            first_skip = int(length * northwest_margin)
            second_skip = int(length * southeast_margin)
            include = length - first_skip - second_skip
            row = 0

            for column in range(start_x, start_x + self.max_x):
                x, y = self._get_coordinates(column, row)

                if self.world_map[y][x].plate == self.id:
                    if first_skip > 0:
                        first_skip -= 1
                    elif include > 0:
                        self.world_map[y][x].ascending_land_check = True
                        include -= 1
                    else:
                        break
                row += 1

    def _descending_land_scan(self) -> None:
        """Scans the plate diagonally, finding valid land positions in northeast to southwest diagonal"""
        if self.type in (constants.NORTH, constants.NORTHEAST, constants.EAST):
            northeast_margin = 0
            southwest_margin = self.margin * 2
        elif self.type in (constants.CENTER, constants.SOUTHEAST, constants.NORTHWEST):
            northeast_margin = self.margin
            southwest_margin = self.margin
        elif self.type in (constants.SOUTH, constants.SOUTHWEST, constants.WEST):
            northeast_margin = self.margin * 2
            southwest_margin = 0

        for start_x, length in self.descending_distance.items():
            first_skip = int(length * northeast_margin)
            second_skip = int(length * southwest_margin)
            include = length - first_skip - second_skip
            row = 0

            for column in range(start_x, start_x - self.max_x, -1):
                x, y = self._get_coordinates(column, row)

                if self.world_map[y][x].plate == self.id:
                    if first_skip > 0:
                        first_skip -= 1
                    elif include > 0:
                        self.world_map[y][x].descending_land_check = True
                        include -= 1
                    else:
                        break
                row += 1

    def _pole_border_correction(self) -> None:
        """Disables globe circling in west end and east end coordinates.
        In function, this should solve continent placement bugs
        which resulted in unexpected water in the far east or west"""
        start = min(self.east_end.keys())
        end = max(self.east_end.keys())

        for y in range(start, end):
            for x in range(self.max_x):
                if self.world_map[y][x].plate == self.id:
                    self.west_end[y] = x
                    break

            for x in range(self.max_x - 1, -1, -1):
                if self.world_map[y][x].plate == self.id:
                    self.east_end[y] = x
                    break

    def create_land(self) -> None:
        """Creates an ocean or continent on this plate, depending on plate type"""
        self.land_area = 0
        self.sea_area = 0

        if self.pole_type != 0:
            self._pole_border_correction()

        if self.type == constants.LAND:
            for region in self.claimed_regions:
                region.terrain = constants.LAND
                self.land_area += region.metrics.area
        elif self.type == constants.WATER:
            for region in self.claimed_regions:
                region.terrain = constants.WATER
                self.sea_area += region.metrics.area
        else:
            if self.type in (
                    constants.CENTER, constants.NORTHEAST, constants.SOUTHEAST,
                    constants.SOUTHWEST, constants.NORTHWEST) or self.pole_type != 0:
                self._horizontal_land_scan()
                self._vertical_land_scan()
            else:
                self._ascending_land_scan()
                self._descending_land_scan()

            for region in self.claimed_regions:
                if (region.horizontal_land_check and region.vertical_land_check) \
                        or (region.ascending_land_check and region.descending_land_check):
                    region.terrain = constants.LAND
                    self.land_area += region.metrics.area
                else:
                    region.terrain = constants.WATER
                    self.sea_area += region.metrics.area

    def sink(self) -> None:
        """Clears all land from this plate. Clears land and sea area calculations"""
        self.land_area = 0
        self.sea_area = 0

        for region in self.claimed_regions:
            region.terrain = constants.WATER
            region.horizontal_land_check = False
            region.vertical_land_check = False
            region.ascending_land_check = False
            region.descending_land_check = False

    def find_boundary_offset(self, distance: int, by_terrain: int) -> list[Region]:
        result = []

        for region in self.claimed_regions:
            if region.north_boundary == region.south_boundary \
                    and region.east_boundary == region.west_boundary:
                continue

            x = region.x
            y = region.metrics.y
            outer_x = region.x
            outer_y = region.metrics.y

            if region.north_boundary and region.south_boundary == False:
                y = region.metrics.y + distance
                outer_y = region.metrics.y - 1
            if region.east_boundary and region.west_boundary == False:
                x = (region.x - distance) % self.max_x
                outer_x = (region.x + 1) % self.max_x
            if region.south_boundary and region.north_boundary == False:
                y = region.metrics.y - distance
                outer_y = region.metrics.y + 1
            if region.west_boundary and region.east_boundary == False:
                x = (region.x + distance) % self.max_x
                outer_x = (region.x - 1) % self.max_x

            if y < 0:
                y = 0
            elif y >= self.max_y:
                y = self.max_y - 1

            outskirts = self.world_map[outer_y][outer_x].terrain

            if by_terrain == outskirts or \
                    (by_terrain == constants.LAND and outskirts == constants.MOUNTAIN):
                # Saves me some calculations
                if distance == 0:
                    result.append(region)
                    continue

                if x != region.x and y != region.metrics.y:
                    # The diagonal alone won't suffice. Take the horizontal and vertical too
                    # Leave a non-mountain margin since distance > 0
                    vertical = self.world_map[region.metrics.y][x]
                    if vertical.plate == self.id and vertical.is_boundary() == False:
                        result.append(vertical)

                    horizontal = self.world_map[y][region.x]
                    if horizontal.plate == self.id and horizontal.is_boundary() == False:
                        result.append(horizontal)

                inner = self.world_map[y][x]
                if inner.plate == self.id and inner.is_boundary() == False:
                    result.append(self.world_map[y][x])
        return result

    def get_info(self) -> str:
        """Returns plate information"""
        west = self._get_circular_coordinate(
            min(self.west_end.values()), self.max_x, True)
        east = self._get_circular_coordinate(
            max(self.east_end.values()), self.max_x, True, True)

        north = self._get_circular_coordinate(
            min(self.north_end.values()), self.max_y, False)
        south = self._get_circular_coordinate(
            max(self.south_end.values()), self.max_y, False, True)

        text = f"""Plate {self.id}
Type: {constants.get_type(self.type)}
Area: {self.area:,} km2
Land area: {self.land_area:,} km2
Sea area {self.sea_area:,} km2
Sea percentage: {self.sea_area / self.area:.0%}
Longitude: {west} to {east}
Latitude: {south} to {north}
Growth: {self.growth}
Sea margin: {self.margin:.0%}"""
        return text
