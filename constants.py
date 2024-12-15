from PyQt5.QtGui import QColor

CENTER = 0
NORTH = 1
NORTHEAST = 2
EAST = 3
SOUTHEAST = 4
SOUTH = 5
SOUTHWEST = 6
WEST = 7
NORTHWEST = 8
LAND = 9
WATER = 10
MOUNTAIN = 11
SHALLOWS = 12
SHORE = 13
DEPTHS = 14
CLIFFS = 15
FLATLAND = 16

PLATE_BORDER_COLOR = QColor(120, 30, 0)
GRID_COLOR = QColor(150, 150, 180)
LINE_COLOR = QColor(90, 90, 120)

COLORS = {WATER: QColor(22, 134, 174), LAND: QColor(189, 171, 123), MOUNTAIN: QColor(118, 108, 93),
          SHALLOWS: QColor(110, 154, 174), SHORE: QColor(162, 139, 100), DEPTHS: QColor(11, 117, 156),
          CLIFFS: QColor(144, 128, 100)}

WORLD = "World"
REGION = "Region"
SUBREGION = "Subregion"
SQUARE_MILE = "Square mile"
SQUARE_KILOMETER = "Square kilometer"


def get_color(terrain: int) -> QColor:
    return COLORS[terrain]


def get_type(type: int) -> str:
    """Translates an integer constant into a string type"""
    type_names = {0: "center", 1: "north", 2: "northeast", 3: "east", 4: "southeast", 5: "south",
                  6: "southwest", 7: "west", 8: "northwest", 9: "land", 10: "water", 11: "mountain"}
    return type_names[type]


def get_type_value(type: str) -> int:
    """Translates a string type into an integer constant"""
    type_values = {"center": 0, "north": 1, "northeast": 2, "east": 3, "southeast": 4, "south": 5,
                   "southwest": 6, "west": 7, "northwest": 8, "land": 9, "water": 10, "mountain": 11}
    return type_values[type.lower()]


def is_type(type: int, cathegory: int):
    """Returns true if type belongs to the given cathegory"""
    if type == cathegory:
        return True
    elif cathegory == LAND:
        return type in (MOUNTAIN, CLIFFS, SHORE)
    elif cathegory == WATER:
        return type in (SHALLOWS, DEPTHS)
    elif cathegory == FLATLAND:
        return type in (LAND, SHORE)


def get_next_coordinates(x: int, y: int, dir: int) -> tuple[int]:
    """Returns new coordinates (x,y) after travelling once in a direction."""
    if dir == NORTH:
        return (x, y-1)
    elif dir == EAST:
        return (x+1, y)
    elif dir == SOUTH:
        return (x, y+1)
    elif dir == WEST:
        return (x-1, y)
    else:
        return (x, y)


def get_next_index(x: int, y: int, dir: int, length: int, height: int) -> tuple[int]:
    """Returns coordinates (x,y) after travelling once in an direction.
    The x-value loops, returning a positive, valid index.
    The y-value doesn't loop, possibly returning an invalid index."""
    nx = x
    ny = y

    if dir in (NORTH, NORTHEAST, NORTHWEST):
        ny -= 1
    elif dir in (SOUTH, SOUTHEAST, SOUTHWEST):
        ny += 1

    if dir in (EAST, NORTHEAST, SOUTHEAST):
        nx += 1
    elif dir in (WEST, NORTHWEST, SOUTHWEST):
        nx -= 1

    nx = nx % length

    return (nx, ny)


def get_side(dir: int, width: int = 1, cell_size: int = 4) -> tuple[int]:
    """Returns coordinates, width and height (x1, y1, w, h) required to draw the edge of a square"""
    if dir == NORTH:
        return (0, 0, cell_size, width)
    elif dir == EAST:
        return (cell_size - width, 0, width, cell_size)
    elif dir == SOUTH:
        return (0, cell_size - width, cell_size, cell_size)
    elif dir == WEST:
        return (0, 0, width, cell_size)


def get_corner(dir: int, cell_size: int = 4) -> tuple[int]:
    """Returns the coordinates (x, y) at the corner of a square"""
    if dir == NORTHEAST:
        return (cell_size - 1, 0)
    elif dir == SOUTHEAST:
        return (cell_size - 1, cell_size - 1)
    elif dir == SOUTHWEST:
        return (0, cell_size - 1)
    elif dir == NORTHWEST:
        return (0, 0)


def get_corner_line(dir: int, distance: int = 1, cell_size: int = 4) -> tuple[int]:
    """Returns the line (x1, y1, x2, y2) cutting of the corner of a square.
    Provide the distance between the corner and line start- / endpoints"""
    if dir == NORTHEAST:
        return (cell_size - 1 - distance, 0, cell_size - 1, distance)
    elif dir == SOUTHEAST:
        return (cell_size - 1, cell_size - 1 - distance, cell_size - 1 - distance, cell_size - 1)
    elif dir == SOUTHWEST:
        return (distance, cell_size - 1, 0, cell_size - 1 - distance)
    elif dir == NORTHWEST:
        return (0, distance, distance, 0)


def within_bounds(x: int, y: int, length: int, height: int) -> bool:
    """Returns true if (x,y) are valid, positive coordinates
    of a two-dimensional list"""
    return (0 <= x < length) and (0 <= y < height)


def flip_direction(dir: int) -> int:
    """Returns the opposite direction"""
    dir += 4
    if dir > 8:
        dir -= 8
    return dir


def turn_direction(dir: int) -> int:
    """Returns the direction with an angle of -90 degrees to the given direction"""
    dir += 2
    if dir > 8:
        dir -= 8
    return dir


def angle_direction(dir: int, steps_of_eight: int) -> int:
    """Rotates a direction in clockwise steps of an eight circle. Returns the new direction"""
    dir += steps_of_eight
    if dir > 8:
        dir -= 8
    return dir


def get_surroundings(x: int, y: int, length: int, height: int) -> list[tuple[int]]:
    """Returns coordinates representing the surroundings of point (x,y) in all eight directions.
    For instance, accessing result[constants.NORTH] will give the coordinates to the north.
    The first item, result[constants.CENTER], is the unmodified (x,y)"""
    result = []

    for dir in range(9):
        result.append(get_next_index(x, y, dir, length, height))

    return result


def get_close_surrondings(x: int, y: int, length: int, height: int) -> list[tuple[int]]:
    """Returns coordinates representing the surroundings of point (x,y) in four directions.
    Returns a list of coordinates, corresponding to directions north, east, south, west,
    in that order"""
    result = []

    for dir in range(1, 8, 2):
        result.append(get_next_index(x, y, dir, length, height))

    return result
