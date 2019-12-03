import socket
import Package

class Network:
    def __init__(self, IP, PORT):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.addr = (IP, PORT)
        self.serverAddr = ('localhost', 5555) # needs to be changed to the server ip


    def send(self, data):
        try:
            dataSent = Package.pack(data, data)
            self.client.sendto(dataSent)

            data, server = self.client.recvfrom(2048)
            dataRecieved = Package.unpack(data)
            return dataRecieved
        except socket.error as error:
            print(str(error))
