from area import Area


class Subregion(Area):
    """Represents an area of 1x1 lat x long, seperated into areas of 10x10 km"""
    # I need 360 of these on a single circle
    # Near the equator, each one should have 11 areas
    # That makes for a total of 3960
    # And an additional 3960 along the other axis
    # Giving an image of 3960x3960
    # Which is fine
    # If I want to go even deeper, I would multiply by 10 again
    # I don't need that kind of resolution on the entire image
    # I may want it on a regional level
    # A region has 5x11x10 = 550
    # Giving an image of 550x550
    # Which is fine

    def __init__(self):
        super().__init__()
