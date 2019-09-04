import socket
import package


class Network:
    def __init__(self, IP, PORT):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.addr = (IP, PORT)
        self.key = self.connect()


    def getKey(self):
        return self.key

    def connect(self):
        try:
            self.client.connect(self.addr)
            data_c = package.unpack(self.client.recv(2048))
            return data_c

        except:
            pass

    def send(self, data):
        try:
            data_s = package.pack(data)
            self.client.send(data_s)

            data_c = package.unpack(self.client.recv(2048))
            return data_c
        except socket.error as error:
            print(str(error))
