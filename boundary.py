from line_generator import LineGenerator
import constants


class Boundary():
    def __init__(self, entrance: int, exit: int, length: int, height: int,
                 primary_terrain: int, secondary_terrain: int, primary_clockwise_to_entry: bool):
        self.path: list[LineGenerator] = []
        self.length = length
        self.height = height
        self.primary_terrain = primary_terrain
        self.secondary_terrain = secondary_terrain
        self.primary_clockwise_to_entry = primary_clockwise_to_entry

        line_generator = LineGenerator(0, 0, length, height)
        line_generator.set_entrance(entrance)
        line_generator.set_exit(exit)
        line_generator.set_terrain(
            primary_terrain, secondary_terrain, primary_clockwise_to_entry)
        line_generator.random_walk()
        self.path.append(line_generator)

    def add_segment(self, exit: int) -> None:
        previous = self.path[-1]
        first = self.path[0]

        x, y = constants.get_next_coordinates(
            previous.x, previous.y, previous.exit)
        line_generator = LineGenerator(x, y, self.length, self.height)
        line_generator.set_entrance(constants.flip_direction(previous.exit))
        line_generator.set_exit(exit)
        line_generator.inherit_start(previous)

        if x == first.x and y == first.y:
            line_generator.inherit_end(first)

        line_generator.set_terrain(self.primary_terrain, self.secondary_terrain,
                                   self.primary_clockwise_to_entry)
        line_generator.random_walk()
        self.path.append(line_generator)
