
class Dto:

    SERVO_X = 'servo_x'
    SERVO_Y = 'servo_y'
    SERVO_Z = 'servo_z'
    HALL = 'hall'
    SENSOR = 'sensor'

    def __init__(self, sensor_name: str = ''):
        self.var = {
            Dto.SENSOR: sensor_name,
            'value': '0',
        }

    def on_scale(self, val):
        self.var['value'] = str(int(val))

