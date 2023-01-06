from threading import Event
import numpy as np
from controller.constants import DTO_Y, DTO_Z, DTO_X
from controller.core_logic.lapshin_algorithm.entity.feature import Feature
from controller.core_logic.scan_algorithms import ScanAlgorithms, FIELD_SIZE
from controller.core_logic.service.scanner_interface import ScannerInterface


class FeatureScanner(ScannerInterface):

    def __init__(self, get_val_func, set_x_func, set_y_func, touching_surface_event: Event, external_surface, push_coord_to_mk, delay: float):
        self.external_surface = external_surface
        self.touching_surface_event = touching_surface_event
        self.set_y_func = set_y_func
        self.set_x_func = set_x_func
        self.get_val_func = get_val_func
        self.push_coord_to_mk = push_coord_to_mk
        self.scan_algorithm = ScanAlgorithms(delay)

    def scan_aria(self, x_min: int = 0, y_min: int = 0, x_max: int = FIELD_SIZE, y_max: int = FIELD_SIZE) -> np.ndarray:
        self.set_x_func(
            (
                x_max,
                self.get_val_func(DTO_Y),
                self.get_val_func(DTO_Z)
            )
        )

        self.push_coord_to_mk(DTO_Z, True)

        self.scan_algorithm.scan_line_by_line(
            self.get_val_func,
            self.set_x_func,
            self.set_y_func,
            self.touching_surface_event,
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

        return self.external_surface[y_min:y_max, x_min:x_max].copy()

    def go_to_feature(self, feature: Feature) -> None:
        self.set_x_func((feature.coordinates[0], feature.coordinates[1], feature.coordinates[2] + 3))
        self.set_y_func((feature.coordinates[0], feature.coordinates[1], feature.coordinates[2] + 3))

    def go_in_direction(self, vector: np.ndarray) -> None:
        z_current = self.get_val_func(DTO_Z)

        self.set_x_func((self.get_val_func(DTO_X) + vector[0], self.get_val_func(DTO_Y), z_current))
        self.set_y_func((self.get_val_func(DTO_X), self.get_val_func(DTO_Y) + vector[1], z_current))

    def switch_scan(self, stop: bool) -> None:
        self.scan_algorithm.stop = stop

    def get_scan_aria_center(self, surface: np.ndarray) -> tuple:
        return (surface.shape[1] - 1) / 2, (surface.shape[0] - 1) / 2
