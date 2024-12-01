from line_generator import LineGenerator
import constants


class Boundary():
    """Used to create a random line. It could be a boundary, circling around
     to its starting point or a path from one point to another"""

    def __init__(self, entrance: int, exit: int, length: int, height: int,
                 line_terrain: int = None, primary_terrain: int = None,
                 secondary_terrain: int = None, line_margin: int = 1,
                 allow_full_turn: bool = True, clockwise_rotation: bool = False):
        """Creates a random line.

        Args:
            entrance:
                direction of the entrance (NORTH, EAST, SOUTH, WEST)
            exit:
                direction of the exit
            length:
                cell length, the area in which a single line segement is contained
            height:
                cell height
            line_terrain:
                terrain of the line (defaults to primary terrain)
            primary_terrain:
                terrain of area within the line
            secondary_terrain:
                terrain of area outside of the line
            line_margin:
                minimum spacing where the line meets itself
                (0 - intersections. 1 - no intersections. 2 - line doesn't meet itself)
            allow_full_turn:
                if false, line cannot go directly against exit
            clockwise_rotation:
                for boundaries creating an enclosed area,
                describes placement of primary terrain relative to entry"""
        self.path: list[LineGenerator] = []
        self.length = length
        self.height = height
        self.primary_terrain = primary_terrain
        self.secondary_terrain = secondary_terrain
        self.line_margin = line_margin
        self.allow_full_turn = allow_full_turn
        self.clockwise_rotation = clockwise_rotation

        if line_terrain is None:
            self.line_terrain = primary_terrain
        else:
            self.line_terrain = line_terrain

        line_generator = LineGenerator(0, 0, length, height, entrance, exit)
        line_generator.random_walk()
        line_generator.paint_terrain(primary_terrain, secondary_terrain,
                                     clockwise_rotation)
        self.path.append(line_generator)

    def add_segment(self, exit: int) -> None:
        previous = self.path[-1]
        first = self.path[0]

        x, y = constants.get_next_coordinates(
            previous.x, previous.y, previous.exit)
        line_generator = LineGenerator(x, y, self.length, self.height,
                                       constants.flip_direction(previous.exit), exit)
        line_generator.inherit_start(previous)

        if x == first.x and y == first.y:
            line_generator.inherit_end(first)

        line_generator.random_walk()
        line_generator.paint_terrain(self.primary_terrain, self.secondary_terrain,
                                     self.clockwise_rotation)
        self.path.append(line_generator)
