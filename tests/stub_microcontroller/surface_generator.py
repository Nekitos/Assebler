import numpy as np
from typing import List, Tuple

MAX_FIELD_SIZE = 76
GENERAL_HEIGHT = 20
ATOMS = [
    (10, 5),
    (10, 15),
    (10, 25),
    (10, 35),
    (10, 45),
    (10, 55),
    (10, 65),
    (20, 10),
    (20, 20),
    (20, 30),
    (20, 40),
    (20, 50),
    (20, 60),
]

# # 1  2  3  4  5  6  7  8  9 10 11 12 13

# [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 1
#  [1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1],  # 2
#  [1, 1, 2, 2, 3, 3, 3, 2, 2, 1, 1, 1, 1],  # 3
#  [1, 1, 2, 3, 4, 4, 4, 3, 2, 1, 1, 1, 1],  # 4
#  [1, 1, 2, 3, 4, 5, 4, 3, 2, 1, 1, 1, 1],  # 5
#  [1, 1, 2, 3, 4, 4, 4, 3, 2, 1, 1, 1, 1],  # 6
#  [1, 1, 2, 2, 3, 3, 3, 2, 2, 1, 1, 1, 1],  # 7
#  [1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1],  # 8
#  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 9
#  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]  # 10

# 3 вида помех:
# 1. Случайный шум
# 2. Смещение всего скана при повторных сканирвоаниях
# 3. Ползучесть в разные стороны зонда во время сканирования
#

class SurfaceGenerator:

    def __init__(self, max_field_size: int, general_height: int, atoms: List[Tuple[int, int]]):
        self.max_field_size = max_field_size
        self.general_height = general_height
        self.atoms = atoms

    def generate(self) -> np.ndarray:
        surface = self.__get_empty_surface()

        return self.__add_atoms(surface, self.atoms)

    def generate_noise_surface(self) -> np.ndarray:
        surface = self.__get_empty_surface()
        surface = self.__add_atoms(surface, self.atoms)
        noise = self.__get_noise()

        return surface + noise

    def __append_atom(self, surface: np.ndarray, x: int, y: int) -> np.ndarray:
        z = surface[y, x]
        surface[(y - 3):(y + 4), (x - 3):(x + 4)] = z + 1
        surface[(y - 3), (x - 3)] = z
        surface[(y + 3), (x + 3)] = z
        surface[(y - 3), (x + 3)] = z
        surface[(y + 3), (x - 3)] = z
        surface[(y - 2):(y + 3), (x - 2):(x + 3)] = z + 2
        surface[(y - 2), (x - 2)] = z + 1
        surface[(y + 2), (x + 2)] = z + 1
        surface[(y - 2), (x + 2)] = z + 1
        surface[(y + 2), (x - 2)] = z + 1
        surface[(y - 1):(y + 2), (x - 1):(x + 2)] = z + 3
        surface[y, x] = z + 4

        return surface

    def __add_atoms(self, surface: np.ndarray, coordinates: List[Tuple[int, int]]):
        for x, y in coordinates:
            try:
                self.__append_atom(surface, x, y)
            except IndexError as e:
                print(str(e))

        return surface

    def __get_empty_surface(self):
        return np.full((self.max_field_size, self.max_field_size), self.general_height)

    def __get_noise(self) -> np.ndarray:
        return np.random.choice([-1, 0, +1], (self.max_field_size, self.max_field_size), replace=True, p=[0.2, 0.6, 0.2])


if __name__ == '__main__':
    print(SurfaceGenerator(20, 1, [(4, 6), (10, 50)]).generate())
