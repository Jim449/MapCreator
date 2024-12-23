from region import Region


class SphereGrid():
    def __init__(self):
        self.content: dict[str, Region] = {}

    def add_cell(self, x: int, y: int, region: Region) -> None:
        self.content[(x, y)] = region

    def get_cell(self, x: int, y: int) -> Region:
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
