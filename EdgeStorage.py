import json
import socket

BUFFERSIZE = 65535
class EdgeStorage:

    def __init__(self,ip,port):
        self.ip=ip
        self.port=port

    def connectToES(self,message):
        try:
            if self.ip == "0" or self.port == 0:
                raise Exception("Edge Storage non presente")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.ip,self.port))
            print("sending to ES {}".format(json.dumps(message,default=str)))
            sock.send(json.dumps(message,default=str).encode()+"\n".encode())
            data = (sock.recv(BUFFERSIZE).decode())
            return data
        except socket.error as ex:
            print("Cannot connect to Edge Storage {}".format(ex))
            raise Exception("{}".format(ex))
        except Exception as ex:
            raise Exception("{}".format(ex))
        finally:
            if self.ip != "0" or self.port != 0:
                sock.close()
    
    def recordContent(self,message):
        message['operation'] = "rec content"
        data = self.connectToES(message)
        return data