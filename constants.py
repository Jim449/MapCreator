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
SHALLOWS_2 = 13

PLATE_BORDER_COLOR = QColor(120, 30, 0)
GRID_COLOR = QColor(150, 150, 180)
LINE_COLOR = QColor(90, 90, 120)

COLORS = {WATER: QColor(22, 134, 174), LAND: QColor(189, 171, 123), MOUNTAIN: QColor(144, 134, 103),
          SHALLOWS: QColor(110, 154, 174)}

REGION = "Region"
SUBREGION = "Subregion"


def get_color(terrain: int) -> QColor:
    return COLORS[terrain]


def get_type(type: int) -> str:
    type_names = {0: "center", 1: "north", 2: "northeast", 3: "east", 4: "southeast", 5: "south",
                  6: "southwest", 7: "west", 8: "northwest", 9: "land", 10: "water", 11: "mountain"}
    return type_names[type]


def get_type_value(type: str) -> int:
    type_values = {"Center": 0, "North": 1, "Northeast": 2, "East": 3, "Southeast": 4, "South": 5,
                   "Southwest": 6, "West": 7, "Northwest": 8, "Land": 9, "Water": 10, "Mountain": 11}
    return type_values[type]


def get_next_coordinates(x: int, y: int, dir: int) -> tuple[int]:
    """Returns new coordinates (x,y) after travelling once in a direction"""
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
