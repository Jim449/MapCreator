from typing import Any


class FlatGrid():
    def __init__(self):
        self.content = {}

    def add_cell(self, x: int, y: int, terrain: int, subregion_x: int, subregion_y: int,
                 subregion_border: bool) -> None:
        self.content[(x, y)] = {"x": x, "y": y, "terrain": terrain,
                                "subregion_x": subregion_x, "subregion_y": subregion_y,
                                "subregion_border": subregion_border}

    def get_cell(self, x: int, y: int) -> dict[str, Any]:
        return self.content[(x, y)]

    def get_all(self, positions: list[tuple[int]]) -> list[dict[str, Any]]:
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

    def filter_terrain(self, terrain: int) -> list[dict[str, Any]]:
        result = []

        for cell in self.content.values():
            if cell["terrain"] == terrain:
                result.append(cell)
