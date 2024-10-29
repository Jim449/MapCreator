class RegionMetrics:
    """Stores region metrics shared by all regions on the same latitude"""

    def __init__(self, area: int, top_stretch: int, bottom_stretch: int, vertical_stretch: int,
                 cost: int, y: int, length_division: int):
        self.area = area
        self.top_stretch = top_stretch
        self.bottom_stretch = bottom_stretch
        self.vertical_stretch = vertical_stretch
        self.cost = cost
        self.y = y
        self.length_division = length_division

        step = 360 // length_division
        self.north = -y * step + 90
        self.south = self.north - step
