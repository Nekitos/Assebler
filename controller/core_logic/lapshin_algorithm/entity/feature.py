

class Feature:

    def __init__(self, coordinates: tuple):
        self.coordinates: tuple = coordinates
        self.max_rad: int = 0
        self.max_height: int = 0
        self.perimeter_len: int = 0
        self.vector_to_next = None
        self.vector_to_prev = None

    def set_coordinates(self, *args):
        self.coordinates = args