from typing import Any


class FlatGrid():
    def __init__(self, subregion_height: int, subregion_count: int):
        self.content: dict[tuple, dict] = {}
        self.subregion_length: list[int] = []
        self.subregion_height: int = subregion_height
        self.subregion_count: int = subregion_count
        self.values = None
        self.index: int = 0

    def add_subregion_length(self, length: int) -> None:
        self.subregion_length.append(length)

    def get_horizontal_stretch(self, index: int) -> int:
        return self.subregion_length[index] * self.subregion_count

    def get_vertical_stretch(self) -> int:
        return self.subregion_height * self.subregion_count

    def get_subregion_length(self, index: int) -> int:
        return self.subregion_length[index]

    def get_subregion_height(self) -> int:
        return self.subregion_height

    def add(self, x: int, y: int, terrain: int) -> None:
        self.content[(x, y)] = {"x": x, "y": y, "terrain": terrain}

    def get(self, x: int, y: int) -> dict[str, int]:
        return self.content[(x, y)]

    def justify_x_right(self, x: int, y: int) -> int:
        return x - self.get_vertical_stretch(y)

    def justify_x_center(self, x: int, y: int) -> int:
        return x - self.get_vertical_stretch(y) // 2

    def get_all(self, positions: list[tuple[int]]) -> list[dict[str, int]]:
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
            result.add(cell["terrain"])

    def filter_terrain(self, terrain: int) -> list[dict[str, int]]:
        result = []

        for cell in self.content.values():
            if cell["terrain"] == terrain:
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
