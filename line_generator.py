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

    def within_center(self, x: int, y: int) -> bool:
        """Checks if a coordinate is in the grid, inside the frame"""
        return (1 <= x < self.length + 1) and (1 <= y < self.height + 1)

    def within_boundaries(self, x: int, y: int) -> bool:
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

    def _next_step(self, walk: list[tuple[int]], opposite_walk: list[tuple[int]]) -> bool:
        """Adds a new position to a walk, so that the walk stays within the given bounds
        and doesn't create loops. If no valid positions are found, both walk and opposite walk
        are cleared, except for their starting points. If walk reaches opposite walk,
        positions are removed from opposite walk until both walks can be joined to form
        a single path.

        Args:
            walk: list of x,y-coordinates
            opposite_walk: list of x,y-coordinates
        Returns:
            True if walk is completed and the two paths can be joined.
            False if walk was either successfully expanded upon or erased 
        """
        x, y = walk[-1]
        options = [constants.NORTH, constants.EAST,
                   constants.SOUTH, constants.WEST]

        while len(options) > 0:
            dir = random.choice(options)
            options.remove(dir)
            next = constants.get_next_coordinates(x, y, dir)

            if next in opposite_walk:
                walk.append(next)
                del opposite_walk[opposite_walk.index(next):]
                return True
            elif self.within_center(next[0], next[1]) and next not in walk:
                walk.append(next)
                return False
        del walk[2:]
        del opposite_walk[2:]
        return False

    def random_walk(self) -> list[tuple]:
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
            if self._next_step(self.forward_walk, self.backward_walk):
                break
            if self._next_step(self.backward_walk, self.forward_walk):
                break

        self.backward_walk.reverse()
        self.forward_walk.extend(self.backward_walk)
        self.backward_walk.clear()
        return self.forward_walk

    def fill_untouched(self, terrain: int) -> None:
        """Fills areas which hasn't yet been filled"""
        for row in self.grid:
            for column in range(self.length):
                if row[column] == -1:
                    row[column] = terrain

    def fill_terrain(self, x: int, y: int, terrain: int) -> None:
        """Fills an area with a terrain"""
        if self.within_boundaries(x, y) == False or self.grid[y][x] != -1:
            return

        self.grid[y][x] = terrain
        self.fill_terrain(x, y - 1, terrain)
        self.fill_terrain(x + 1, y, terrain)
        self.fill_terrain(x, y + 1, terrain)
        self.fill_terrain(x - 1, y, terrain)

    def paint_terrain(self, primary_terrain: int, secondary_terrain: int,
                      primary_clockwise_to_entry: bool = False, fill_remains: bool = True) -> None:
        for row in range(self.height + 2):
            self.grid.append([-1 for column in range(self.length + 2)])

        for x, y in self.forward_walk:
            self.grid[y][x] = primary_terrain

        next_dir = (self.entrance + 2) % 8
        final_dir = (self.exit + 2) % 8

        next_x, next_y = constants.get_next_coordinates(
            self.prior_x, self.prior_y, next_dir)
        last_x, last_y = constants.get_next_coordinates(
            self.post_x, self.post_y, final_dir)

        if primary_clockwise_to_entry:
            self.fill_terrain(next_x, next_y, primary_terrain)
            self.fill_terrain(last_x, last_y, secondary_terrain)
        else:
            self.fill_terrain(next_x, next_y, secondary_terrain)
            self.fill_terrain(last_x, last_y, primary_terrain)

        if fill_remains:
            self.fill_untouched(primary_terrain)


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
