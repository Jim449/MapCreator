from typing import Self
import random
import constants


class LineGenerator():
    """Used for creating random paths or borders.
    The LineGenerator describes the area where the path should be created.
    When creating borders, a LineGenerator typically describes
    the intersection between for cells (regions, subregions etc.)
    In other words, it's a cell offset by 0.5 length x and 0.5 height y."""

    def __init__(self, x: int, y: int, length: int, height: int,
                 entrance: int, exit: int):
        """Creates a line generator cell at x, y"""
        self.x = x
        self.y = y
        self.length = length
        self.height = height
        self.entrance = entrance
        self.exit = exit
        self.start_x = -1
        self.start_y = -1
        self.prior_x = -1
        self.prior_y = -1
        self.end_x = -1
        self.end_y = -1
        self.post_x = -1
        self.post_y = -1
        self.forward_walk: list[tuple[int]] = []
        self.backward_walk: list[tuple[int]] = []
        self.grid: list[list[int]] = []

    def _within_center(self, x: int, y: int) -> bool:
        """Checks if a coordinate is in the grid, inside the frame"""
        return (1 <= x < self.length + 1) and (1 <= y < self.height + 1)

    def _within_boundaries(self, x: int, y: int) -> bool:
        """Checks if a coordinate is contained within the grid"""
        return (0 <= x < self.length + 2) and (0 <= y < self.height + 2)

    def set_entrance(self, direction: int) -> None:
        """Sets the direction of the previous offset cell"""
        self.entrance = direction

    def set_exit(self, direction: int) -> None:
        """Sets the direction of the next offset cell"""
        self.exit = direction

    def _generate_points(self, direction: int) -> tuple[int]:
        """Given an entrance or exit direction, generates start or end coordinates.
        Returns (start/end x, start/end y, prior/post x, prior/post y)"""
        if direction == constants.NORTH:
            x = random.randrange(1, self.length + 1)
            prior_x = x
            y = 1
            prior_y = 0
        elif direction == constants.EAST:
            x = self.length
            prior_x = self.length + 1
            y = random.randrange(1, self.height + 1)
            prior_y = y
        elif direction == constants.SOUTH:
            x = random.randrange(1, self.length + 1)
            prior_x = x
            y = self.height
            prior_y = self.height + 1
        elif direction == constants.WEST:
            x = 1
            prior_x = 0
            y = random.randrange(1, self.height + 1)
            prior_y = y
        return (x, y, prior_x, prior_y)

    def generate_start(self) -> None:
        """Generates starting coordinates of a boundary,
        based on the direction of the entrance"""
        self.start_x, self.start_y, self.prior_x, self.prior_y = self._generate_points(
            self.entrance)

    def generate_end(self) -> None:
        """Generates ending coordinates of a boundary
        based on the direction of the exit"""
        self.end_x, self.end_y, self.post_x, self.post_y = self._generate_points(
            self.exit)

    def inherit_start(self, predecessor: Self) -> None:
        """Sets the starting coordinates of a boundary
        based on the ending coordinates of the predecessors boundary"""
        self.prior_x = predecessor.post_x
        self.prior_y = predecessor.post_y

        if self.prior_x == 0:
            self.prior_x = self.length + 1
        elif self.prior_x == self.length + 1:
            self.prior_x = 0
        elif self.prior_y == 0:
            self.prior_y = self.height + 1
        elif self.prior_y == self.height + 1:
            self.prior_y = 0

        self.start_x, self.start_y = constants.get_next_coordinates(
            self.prior_x, self.prior_y, predecessor.exit)

    def inherit_end(self, originator: Self) -> None:
        """Sets the ending coordinates of a boundary
        based on the starting coordinates of the first offset cell of the loop"""
        self.post_x = originator.prior_x
        self.post_y = originator.prior_y

        if self.post_x == 0:
            self.post_x = self.length + 1
        elif self.post_x == self.length + 1:
            self.post_x = 0
        elif self.post_y == 0:
            self.post_y = self.height + 1
        elif self.post_y == self.height + 1:
            self.post_y = 0

        self.end_x, self.end_y = constants.get_next_coordinates(
            self.post_x, self.post_y, originator.entrance)

    def _margin_check(self, step: tuple[int], walk: list[tuple[int]],
                      margin: int, direction: int) -> bool:
        """Return true if the given step has sufficient margins
        to previous steps within the same walk.
        Provide direction of travel from the previous step"""
        if margin == 0:
            return True
        elif margin == 1:
            return step not in walk
        elif margin == 2:
            backwards = constants.flip_direction(direction)

            for dir in range(1, 8, 2):
                if dir == backwards:
                    continue
                coordinates = constants.get_next_coordinates(
                    step[0], step[1], dir)

                if coordinates in walk:
                    return False
            return True

    def _completion_check(self, walk: list[tuple[int]], opposite: list[tuple[int]],
                          directions: list[int]) -> bool:
        """Checks if a walk can reach the opposite walk within a single step.
        Adds that step to the walk and returns true.
        If opposite walk is unreachable, returns false"""
        last = walk[-1]

        for dir in directions:
            coordinates = constants.get_next_coordinates(last[0], last[1], dir)

            if coordinates in opposite:
                walk.append(coordinates)
                return True
        return False

    def _next_step(self, walk: list[tuple[int]],
                   opposite_walk: list[tuple[int]],
                   margin: int, forbid_turn: bool,
                   banned_direction: int) -> bool:
        """Adds a new position to a walk, so that the walk stays within the given bounds.
        If no valid positions are found, both walk and opposite walk
        are cleared, except for their starting points. If walk reaches opposite walk,
        positions are removed from opposite walk until both walks can be joined to form
        a single path.

        Args:
            walk: list of x,y-coordinates
            opposite_walk: list of x,y-coordinates
            margin: walks minimum distance to self. 0: loops allowed. 1: loops forbidden. 2: no enclosed areas
            forbid_turn: ban walks moving directly away from exit direction
            banned_direction: direction banned by forbid_turn
        Returns:
            True if walk is completed and the two paths can be joined.
            False if walk was either successfully expanded upon or erased 
        """
        x, y = walk[-1]
        options = [constants.NORTH, constants.EAST,
                   constants.SOUTH, constants.WEST]

        if forbid_turn:
            options.remove(banned_direction)

        # For margin of 2, walk can only approach the opposite walk
        # for the purpose of completing the walk
        if margin == 2 and self._completion_check(walk, opposite_walk, options):
            last = walk[-1]
            del opposite_walk[opposite_walk.index(last):]
            return True

        while len(options) > 0:
            dir = random.choice(options)
            options.remove(dir)
            next = constants.get_next_coordinates(x, y, dir)

            if next in opposite_walk:
                walk.append(next)
                del opposite_walk[opposite_walk.index(next):]
                return True

            elif self._within_center(next[0], next[1]):
                if self._margin_check(next, walk, margin, dir):
                    walk.append(next)
                    return False

        del walk[2:]
        del opposite_walk[2:]
        return False

    def random_walk(self, margin: int = 1, forbid_turn: bool = False) -> list[tuple]:
        """Generates a random path from start to end coordinates.
        The path will be free of loops"""
        if self.start_x == -1:
            self.generate_start()
        if self.end_x == -1:
            self.generate_end()

        self.forward_walk = [(self.prior_x, self.prior_y),
                             (self.start_x, self.start_y)]
        self.backward_walk = [(self.post_x, self.post_y),
                              (self.end_x, self.end_y)]

        while True:
            if self._next_step(self.forward_walk, self.backward_walk, margin,
                               forbid_turn, constants.flip_direction(self.exit)):
                break
            if self._next_step(self.backward_walk, self.forward_walk, margin,
                               forbid_turn, self.exit):
                break

        self.backward_walk.reverse()
        self.forward_walk.extend(self.backward_walk)
        self.backward_walk.clear()
        return self.forward_walk

    def _fill_untouched(self, terrain: int) -> None:
        """Fills areas which hasn't yet been filled"""
        for row in self.grid:
            for column in range(self.length):
                if row[column] == -1:
                    row[column] = terrain

    def _fill_terrain(self, x: int, y: int, terrain: int) -> None:
        """Fills an area with a terrain"""
        if self._within_boundaries(x, y) == False or self.grid[y][x] != -1:
            return

        self.grid[y][x] = terrain
        self.fill_terrain(x, y - 1, terrain)
        self.fill_terrain(x + 1, y, terrain)
        self.fill_terrain(x, y + 1, terrain)
        self.fill_terrain(x - 1, y, terrain)

    def _strip_grid(self):
        """Removes the outer elements of the grid"""
        self.grid.pop()
        self.grid.pop(0)

        for row in self.grid:
            row.pop()
            row.pop(0)

    def paint_terrain(self, line_terrain: int,
                      primary_terrain: int = -1,
                      secondary_terrain: int = -1,
                      primary_clockwise_to_entry: bool = False,
                      fill_remains: bool = True) -> None:
        """Paints the terrain.

        Args:
            line_terrain:
                terrain for painting the path
            primary_terrain:
                terrain for painting the area enclosed by the boundary or -1 for no paint
            secondary_terrain:
                terrain for painting the area outside the boundary or -1 for no paint
            primary_clockwise_to_entry:
                position of primary terrain relative to entrance direction.
                Typically, the enclosed area is clockwise, making this counter clockwise
            fill_remains:
                if true, fills unpainted areas with primary terrain.
                Handles areas the fill algorithm missed"""
        for row in range(self.height + 2):
            self.grid.append([-1 for column in range(self.length + 2)])

        for x, y in self.forward_walk:
            self.grid[y][x] = line_terrain

        next_dir = (self.entrance + 2) % 8
        final_dir = (self.exit + 2) % 8

        next_x, next_y = constants.get_next_coordinates(
            self.prior_x, self.prior_y, next_dir)
        last_x, last_y = constants.get_next_coordinates(
            self.post_x, self.post_y, final_dir)

        if primary_terrain != -1:
            if primary_clockwise_to_entry:
                self._fill_terrain(next_x, next_y, primary_terrain)
            else:
                self._fill_terrain(last_x, last_y, primary_terrain)

        if secondary_terrain != -1:
            if primary_clockwise_to_entry:
                self._fill_terrain(last_x, last_y, secondary_terrain)
            else:
                self._fill_terrain(next_x, next_y, secondary_terrain)

        if primary_terrain != -1 and fill_remains:
            self._fill_untouched(primary_terrain)

        self._strip_grid()

    def clear(self) -> None:
        """Removes generated terrain while retaining position in boundary"""
        self.start_x = -1
        self.start_y = -1
        self.prior_x = -1
        self.prior_y = -1
        self.end_x = -1
        self.end_y = -1
        self.post_x = -1
        self.post_y = -1
        self.forward_walk.clear()
        self.backward_walk.clear()
        self.grid.clear()

    def get_terrain_grid(self) -> list[list[int]]:
        """Returns the terrain grid"""
        return self.grid

    def get_grid_offset(self) -> tuple[int, int]:
        """Returns the in-world coordinate (x, y)
        pointed at by the grid element at (0, 0)"""
        return (self.x, self.y)


if __name__ == "__main__":
    northeast = LineGenerator(1, 0, 5, 5, constants.WEST, constants.SOUTH)
    northeast.random_walk()
    northeast.set_terrain(1, 0, False)

    southeast = LineGenerator(1, 1, 5, 5, constants.NORTH, constants.WEST)
    southeast.inherit_start(northeast)
    southeast.random_walk()
    southeast.set_terrain(1, 0, False)

    southwest = LineGenerator(0, 1, 5, 5, constants.WEST, constants.NORTH)
    southwest.inherit_start(southeast)
    southwest.random_walk()
    southwest.set_terrain(1, 0, False)

    northwest = LineGenerator(0, 0, 5, 5, constants.SOUTH, constants.EAST)
    northwest.inherit_start(southwest)
    northwest.inherit_end(northeast)
    northwest.random_walk()
    northwest.set_terrain(1, 0, False)

    for location in northeast.forward_walk:
        print(f"({location[0]}, {location[1]})", end=" ")
    print(f"from ({northeast.prior_x},{northeast.prior_y}) to ({
          northeast.post_x},{northeast.post_y})")

    for location in southeast.forward_walk:
        print(f"({location[0]}, {location[1]})", end=" ")
    print(f"from ({southeast.prior_x},{southeast.prior_y}) to ({
          southeast.post_x},{southeast.post_y})")

    for location in southwest.forward_walk:
        print(f"({location[0]}, {location[1]})", end=" ")
    print(f"from ({southwest.prior_x},{southwest.prior_y}) to ({
          southwest.post_x},{southwest.post_y})")

    for location in northwest.forward_walk:
        print(f"({location[0]}, {location[1]})", end=" ")
    print(f"from ({northwest.prior_x},{northwest.prior_y}) to ({
          northwest.post_x},{northwest.post_y})")
    print()

    for row in northeast.grid:
        for x in row:
            print(x, end="")
        print()
    print()

    for row in southeast.grid:
        for x in row:
            print(x, end="")
        print()
    print()

    for row in southwest.grid:
        for x in row:
            print(x, end="")
        print()
    print()

    for row in northwest.grid:
        for x in row:
            print(x, end="")
        print()
