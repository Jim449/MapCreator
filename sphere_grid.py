from region import Region


class SphereGrid():
    def __init__(self):
        self.content: dict[tuple, Region] = {}
        self.values = None
        self.index: int = 0

    def add(self, x: int, y: int, region: Region) -> None:
        self.content[(x, y)] = region

    def get(self, x: int, y: int) -> Region:
        return self.content[(x, y)]

    def get_all(self, positions: list[tuple[int]]) -> Region:
        result = []

        for coordinates in positions:
            try:
                result.append(self.content[coordinates])
            except IndexError:
                result.append(None)

        return result

    def get_unique_terrain(self) -> list[int]:
        result = set()

        for cell in self.content.values():
            result.add(cell.terrain)

    def filter_terrain(self, terrain: int) -> list[Region]:
        result = []

        for cell in self.content.values():
            if cell.terrain == terrain:
                result.append(cell)

    def __iter__(self):
        self.values = self.content.values()
        self.index = 0
        return self

    def __next__(self):
        try:
            item = self.values[self.index]
            self.index += 1
            return item
        except IndexError:
            raise StopIteration
