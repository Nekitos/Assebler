from typing import List, Tuple
import json
import numpy as np
from controller.constants import *
from controller.core_logic.atom import Atom
from controller.core_logic.dto import Dto
from controller.core_logic.tool import Tool
from sockets.server import Server

INVALID_DTO = "Invalid dto"


class AtomsLogic:

    def __init__(
            self,
            x_field_size: int = MAX_FIELD_SIZE,
            y_field_size: int = MAX_FIELD_SIZE,
            server=Server,
    ):
        self.surface_data = np.zeros((x_field_size, y_field_size))
        self.atom_captured_event: bool = False
        self.atom_release_event: bool = False
        self.append_unique_atom_event: bool = False
        self.__tool = Tool()
        self.dto_x = Dto(Dto.SERVO_X, self.surface_data, self.__tool)
        self.dto_y = Dto(Dto.SERVO_Y, self.surface_data, self.__tool)
        self.dto_z = Dto(Dto.SERVO_Z, self.surface_data, self.__tool)
        self.dto_z.set_val((0, 0, MAX))
        self.server = server(self.handle_server_data)
        self.atoms_list: List[Atom] = []  # todo вынести это и все связанный методы в одельный класс AtomCollection

    def tool_is_coming_down(self):
        return self.__tool.is_coming_down

    def is_scan_mode(self):
        return self.__tool.scan_mode

    def set_scan_mode(self, pred: bool) -> None:
        self.__tool.scan_mode = pred

    def set_val_to_dto(self, dto_str: str, coordinates: Tuple[int, int, int]):
        coordinates_int = tuple(map(int, coordinates))
        dto_name = 'dto_' + dto_str
        dto = getattr(self, dto_name, INVALID_DTO)
        if dto == INVALID_DTO:
            raise ValueError(dto)
        dto.validate_val(coordinates_int)
        if self.__tool.scan_mode and dto_str == DTO_Z:
            self.__update_existing_surface(coordinates_int)
        dto.set_val(coordinates_int)

    def __update_existing_surface(self, coordinates: Tuple[int, ...]) -> None:  # todo заменить второе условие на self.__tool.is_coming_down после тостов
        if not self.__tool.is_it_surface \
                and coordinates[2] < self.dto_z.get_val() \
                and int(self.surface_data.item((coordinates[1], coordinates[0]))) > coordinates[2]:
            self.surface_data[coordinates[1], coordinates[0]] = coordinates[2] - CORRECTION_Z

    def handle_server_data(self, data: str):
        data_dict = self.parse_server_data(data, 0)
        if data_dict == False:
            return
        if self.__tool.scan_mode and self.__tool.is_coming_down and data_dict['sensor'] == 'surface':
            self.set_is_it_surface(bool(data_dict['val']))
            self.build_new_surface()
        if data_dict['sensor'] == 'atom':  # todo это будет событие atom_captured
            print('atom')
            self.set_is_it_atom(bool(data_dict['val']))

    def parse_server_data(self, data: str, i: int):
        try:
            data_dict = json.loads(data)
        except Exception:
            json_str = f"{data.split('}')[i]}}}"
            i += 1
            if i > 1:
                return False
            data_dict = self.parse_server_data(json_str, i)  # todo передавать сюда data.split('}')[i]
        return data_dict

    def build_new_surface(self):
        if self.is_it_surface():
            self.surface_data[self.dto_y.get_val(), self.dto_x.get_val()] = self.dto_z.get_val() - CORRECTION_Z

    def is_it_surface(self) -> bool:
        return self.__tool.is_it_surface

    def set_is_it_surface(self, pred: bool):
        self.__tool.is_it_surface = pred

    def is_it_atom(self) -> bool:
        return self.__tool.is_it_atom

    def set_is_it_atom(self, pred: bool):
        self.__tool.is_it_atom = pred

    def append_unique_atom(self) -> bool:
        atom = Atom(self.get_tool_coordinate())
        if not self.__tool.is_atom_captured and not atom in self.atoms_list:
            self.atoms_list.append(atom)
            return True

        return False

    def is_atom_captured(self) -> bool:
        return self.__tool.is_atom_captured

    def set_is_atom_captured(self, pred: bool):
        if pred and not self.__tool.is_atom_captured:
            self.mark_atom_capture()
            self.atom_captured_event = True
        if self.__tool.is_atom_captured and not pred:
            self.mark_atom_release()
            self.atom_release_event = True
        self.__tool.is_atom_captured = pred

    def is_new_point(self) -> bool:
        return (self.dto_x.get_val() != self.__tool.x or self.dto_y.get_val() != self.__tool.y or self.dto_z.get_val() != self.__tool.z) and \
               ((self.dto_x.get_val() % MULTIPLICITY == 0) or (self.dto_y.get_val() % MULTIPLICITY == 0) or (self.dto_z.get_val() % MULTIPLICITY == 0))

    def update_tool_coordinate(self):
        self.__set_command_to_microcontroller()
        self.__tool.x = self.dto_x.get_val()
        self.__tool.y = self.dto_y.get_val()
        self.__tool.z = self.dto_z.get_val()

    def get_tool_coordinate(self):
        return self.__tool.x, self.__tool.y, self.__tool.z

    def __set_command_to_microcontroller(self):
        if self.dto_x.get_val() != self.__tool.x:
            self.server.send_data_to_all_clients(json.dumps(self.dto_x.to_dict()))
            return
        if self.dto_y.get_val() != self.__tool.y:
            self.server.send_data_to_all_clients(json.dumps(self.dto_y.to_dict()))
            return
        if self.dto_z.get_val() != self.__tool.z:
            data = self.__invert_data(self.dto_z.to_dict())
            self.server.send_data_to_all_clients(json.dumps(data))
            return

    @staticmethod
    def __invert_data(data: dict):
        data['value'] = str(MAX - int(data['value']))
        return data

    def mark_atom_capture(self) -> None:
        for atom in self.atoms_list:
            is_x_in = atom.coordinates[0] in range(self.__tool.x - 1, self.__tool.x + 2)
            is_y_in = atom.coordinates[1] in range(self.__tool.y - 1, self.__tool.y + 2)
            is_z_in = atom.coordinates[2] in range(self.__tool.z - 3, self.__tool.z + 1)
            if is_x_in and is_y_in and is_z_in:
                atom.is_captured = True
                break

    def mark_atom_release(self):
        for atom in self.atoms_list:
            if atom.is_captured:
                atom.set_coordinates(self.__tool.x, self.__tool.y, self.__tool.z)
                atom.is_captured = False
                return

    def get_dto_val(self, dto_str: str) -> int:
        dto_name = 'dto_' + dto_str
        dto = getattr(self, dto_name, INVALID_DTO)
        if dto == INVALID_DTO:
            raise ValueError(dto)
        return dto.get_val()

    def set_val_dto_curried(self, dto_str: str):
        def wrap(coordinates: Tuple[int, int, int]):
            self.set_val_to_dto(dto_str, coordinates)
        return wrap
