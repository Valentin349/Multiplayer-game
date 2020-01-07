import socket
import Package


class Network:
    def __init__(self, PORT):
        self.ip = self.searchNetwork()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.addr = (self.ip, PORT)
    def send(self, data):
        try:
            dataSent = Package.pack(data)
            self.client.sendto(dataSent, self.addr)
            
            data, server = self.client.recvfrom(2048)
            dataRecieved = Package.unpack(data)
            return dataRecieved
        except socket.error as error:
            print(str(error))

    def searchNetwork(self):
        port = 5544
        for ending in range(0, 20):
            addr = socket.gethostbyname(socket.gethostname())[:-2] + str(ending)
            print(addr)
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(0.5)
            result = conn.connect_ex((addr, port))
            conn.close()

            if result == 0:
                socket.setdefaulttimeout(None)
                return addr