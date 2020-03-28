import socket
import Package


class Network:
    """ Network class used to send and recieve data from a server.
        Data which is sent is in form of a JSON and is encoded before being sent,
        received data is decoded and passed on. All data except for requests is JSON"""
    def __init__(self):
        #sets up a UDP socket to communicate with server on port 555
        self.PORT = 5555
        self.ip = None
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(2)

    def send(self, data):
        addr = (self.ip, self.PORT)
        try:
            dataSent = Package.pack(data)
            self.client.sendto(dataSent, addr)
            #data received from server along with address
            data, server = self.client.recvfrom(2048)
            dataRecieved = Package.unpack(data)
            return dataRecieved
        except socket.timeout:
            #if a the client waits longer than 2 seconds it assumes host disconnected
            self.exit()

    def exit(self):
        self.ip = None

    def leaveRequest(self):
        #notifies the server that client is leaving
        try:
            self.send("ExitRequest")
        except:
            pass

    def searchNetwork(self):
        port = 5544
        result = None
        subnet = ".".join(socket.gethostbyname(socket.gethostname()).split(".")[:-1]) + "."
        #checks ip addresses similar to the user ip address

        for ending in range(0, 255):
            addr = subnet + str(ending)
            print(addr)
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(0.1)
            result = conn.connect_ex((addr, port))
            conn.close()

            if result == 0:
                socket.setdefaulttimeout(None)
                return addr
        if result != 0:
            return None
