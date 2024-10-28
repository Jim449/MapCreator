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


def get_type(type: int) -> str:
    type_names = {0: "center", 1: "north", 2: "northeast", 3: "east", 4: "southeast", 5: "south",
                  6: "southwest", 7: "west", 8: "northwest", 9: "land", 10: "water", 11: "mountain"}
    return type_names[type]
