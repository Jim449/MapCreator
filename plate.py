from region import Region
import random
import constants


class Plate():
    def __init__(self, id: int, world_map: list[list[Region]], start_x: int, start_y: int,
                 type: int = constants.CENTER, margin: float = 0.25, island_rate: float = 0.1,
                 growth: int = 4):
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

        self.currency: float = growth
        self.alive: bool = True
        self.area: int = 0
        self.land_area: int = 0
        self.sea_area: int = 0
        self.pole_type: int = 0
        self.claimed_regions: list[Region] = []

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
        Give direction north=0, east=1, south=2, west=3"""
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
        """Updates boundaries.

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

    def claim_region(self, x: int, y: int) -> None:
        """Claims a region. Updates plate boundaries and pays region cost"""
        ix, iy = self._get_coordinates(x, y)
        region = self.world_map[iy][ix]
        region.plate = self.id
        region.plate_x = x
        region.plate_y = y
        region.active = False
        region.alive = True
        self.area += region.metrics.area
        self.currency -= region.metrics.cost
        self.claimed_regions.append(region)
        self._set_boundary(self.west_end, self.east_end, y, x)
        self._set_boundary(self.north_end, self.south_end, x, y)

    def claim_pole(self, y: int) -> None:
        """Claims an entire horizontal circle at a pole.
        Updates plate boundaries and pays region costs"""
        for x in range(self.max_x):
            self.claim_region(x, y)

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
        for region in self.claimed_regions:
            if region.alive:
                region.active = True
                amount += 1
        return amount

    def restore(self) -> None:
        """Restore expansion power"""
        self.currency += self.growth

    def expand(self) -> int:
        """Expands the plate in random directions,
        using currency and claimed region sizes to determine when to stop.
        Returns remaining currency.
        Plate is expanded only from regions claimed before method call.
        If returned currency is positive, call again to complete expansion
        """
        active_regions = self._awaken_regions()

        if active_regions == 0:
            self.alive = False
            return 0

        random.shuffle(self.claimed_regions)

        # Possible to loop over claimed regions while adding new regions to the list?
        for region in self.claimed_regions:
            if self.currency <= 0 or active_regions == 0:
                return self.currency
            elif not region.active:
                continue

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
            region.alive = False
            active_regions -= 1
        return self.currency

    def _horizontal_land_scan(self):
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
            length = self.south_end[column] - self.north_end[column]
            start = self.north_end[column] + int(length * north_margin)
            end = self.south_end[column] - int(length * south_margin)

            for row in range(start, end + 1):
                x, y = self._get_coordinates(column, row)
                if self.world_map[y][x].plate == self.id:
                    self.world_map[y][x].horizontal_land_check = True

    def _vertical_land_scan(self):
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
            length = self.east_end[row] - self.west_end[row]
            start = self.west_end[row] + int(length * west_margin)
            end = self.east_end[row] - int(length * east_margin)

            for column in range(start, end + 1):
                x, y = self._get_coordinates(column, row)
                if self.world_map[y][x].plate == self.id:
                    self.world_map[y][x].vertical_land_check = True

    def create_land(self):
        """Creates an ocean or continent on this plate, depending on plate type"""
        if self.type == constants.LAND:
            for region in self.claimed_regions:
                region.terrain = constants.LAND
                self.land_area += region.metrics.area
        elif self.type == constants.WATER:
            for region in self.claimed_regions:
                region.terrain = constants.WATER
                self.sea_area += region.metrics.area
        else:
            self._horizontal_land_scan()
            self._vertical_land_scan()

            for region in self.claimed_regions:
                if region.horizontal_land_check and region.vertical_land_check:
                    region.terrain = constants.LAND
                    self.land_area += region.metrics.area
                else:
                    region.terrain = constants.WATER
                    self.sea_area += region.metrics.area

    def get_info(self) -> str:
        if self.pole_type != 0:
            west = -180
            east = 180
        else:
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
