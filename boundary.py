from line_generator import LineGenerator
import constants


class Boundary():
    """Used to create a random line. It could be a boundary, circling around
     to its starting point or a path from one point to another"""

    def __init__(self, entrance: int, exit: int, length: int, height: int,
                 start_x: int, start_y: int,
                 line_terrain: int = -1, primary_terrain: int = -1,
                 secondary_terrain: int = -1, line_margin: int = 1,
                 forbid_full_turn: bool = False, clockwise_rotation: bool = False,
                 enclosing: bool = True):
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
        self.start_x = start_x
        self.start_y = start_y
        self.primary_terrain = primary_terrain
        self.secondary_terrain = secondary_terrain
        self.line_margin = line_margin
        self.forbid_full_turn = forbid_full_turn
        self.clockwise_rotation = clockwise_rotation
        self.enclosing = enclosing

        if line_terrain == -1:
            self.line_terrain = primary_terrain
        else:
            self.line_terrain = line_terrain

        line_generator = LineGenerator(0, 0, length, height, entrance, exit)
        self.path.append(line_generator)

    def add_segment(self, exit: int) -> None:
        """Adds a new segment to the path, with an exit in the given direction"""
        previous = self.path[-1]

        x, y = constants.get_next_coordinates(
            previous.x, previous.y, previous.exit)
        line_generator = LineGenerator(x, y, self.length, self.height,
                                       constants.flip_direction(previous.exit), exit)
        self.path.append(line_generator)

    def clear_path(self):
        """Clears the generated path and retain, retaining the general stretch of the path"""
        for segment in self.path:
            segment.clear()

    def generate(self):
        """Generates paths and terrain for this boundary"""
        segment = self.path[0]
        segment.random_walk(self.line_margin, self.forbid_full_turn)
        segment.paint_terrain(
            self.line_terrain, self.primary_terrain, self.secondary_terrain)

        for index in range(1, len(self.path) - 1):
            previous = segment
            segment = self.path[index]
            segment.inherit_start(previous)
            segment.random_walk(self.line_margin, self.forbid_full_turn)
            segment.paint_terrain(
                self.line_terrain, self.primary_terrain, self.secondary_terrain)

        last = self.path[-1]
        last.inherit_start(segment)

        if self.enclosing:
            last.inherit_end(self.path[0])

        last.random_walk(self.line_margin, self.forbid_full_turn)
        last.paint_terrain(self.line_terrain,
                           self.primary_terrain, self.secondary_terrain)
