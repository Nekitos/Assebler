from servoController import ServoController
from client_socket.mySocket import Socket
import ujson
import sys


class Client(Socket):
    def __init__(self):
        super(Client, self).__init__()
        self.data_prev = ''
        self.type_object = 'Client'
        self.servoController = ServoController()

    def set_up(self):
        try:
            self.connect((self.IP, self.PORT))
        except Exception as e:
            self.status = 'Server is offline'
            print(str(e))
            sys.exit(0)
        self.listen_server()

    def listen_server(self):
        while not self._quit:
            try:
                self.data = self.recv(self.PACKAGE_SIZE).decode(self.CODING)
                if self.data == self.CONNECTED:
                    self.status = self.CONNECTED
                self.send_data('hi_esp8266')
                if (self.data_prev != self.data) and (self.CONNECTED != self.data):
                    try:
                        parsed = ujson.loads(self.data)
                        self.servoController.process_data(parsed)
                    except ValueError as e:
                        print(str(e))
                    finally:
                        self.data_prev = self.data
            except Exception as e:
                print(str(e))
                self.set_down()
                break

    def send_data(self, data: str):
        try:
            self.send(data.encode(self.CODING))
        except:
            self.set_down()


if __name__ == '__main__':
    client = Client()
    client.set_up()
