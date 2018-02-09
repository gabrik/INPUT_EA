#!/usr/bin/python3
import socket
import threading
import signal
import utility
import os
import json
import base64
import sys
import configparser
import traceback
from utility import bcolors
from Database import Database
from EdgeStorage import EdgeStorage



class EdgeAcquirer(object):
    pid = {}
    def __init__(self, host, port, nomeDb, ip, dbport, username, password,ipStorage,portStorage):
        try:
            os.remove("ffconf/ffserver.out")
        except Exception as ex:
            print("File non presenti ")
        self.database = Database(nomeDb,ip,dbport,username,password)
        utility.createffserverconf(self.database.getProvidersKeys())
        self.pid[self.startFFserver()] = "ffserver"
        signal.signal(signal.SIGINT, self.stopEdgeAcquirer)
        signal.signal(signal.SIGCHLD, self.restartChild)
        self.es=EdgeStorage(ipStorage,portStorage)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))

    def startFFserver(self):
        pid = os.fork()
        if pid < 0:
            print("cannot fork process")
            exit()
        elif pid == 0:
            fp = os.open("ffconf/ffserver.out", os.O_WRONLY|os.O_CREAT)
            os.dup2(fp, sys.stdout.fileno())
            os.dup2(fp, sys.stderr.fileno())
            os.execvp("ffserver", ["ffserver", "-hide_banner", "-loglevel",
                                   "panic", "-f", "ffconf/ffserver.conf", "-d"])
        else:
            print("FFserver started with pid {}".format(pid))
        return pid

    def restartChild(self, signum,stack):
        pid, sts = os.waitpid(-1, os.WNOHANG)
        if pid in self.pid:
            if self.pid[pid] == "ffserver":
                print("FFserver {} stopped restarting it", format(self.pid[pid]))
                self.pid[self.startFFserver()] = "ffserver"
    
    def stopEdgeAcquirer(self, signum,stack):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        for pid in list(self.pid.keys()):
            os.kill(pid, signal.SIGINT)
            print("Edge Acquirer stopped")
            exit()

    def listen(self):
        self.sock.listen(5)
        print("EdgeAcquirer ready to accept")
        while True:
            client, address = self.sock.accept()
            print("New connection from {}".format(address))
            #client.settimeout(60)
            threading.Thread(target = self.listenToClient, args = (client, address)).start()

    def preSend(self, jsonlist):
        for f in jsonlist:
            image = f["image"]
            jpgtxt = base64.b64encode(open(image, "rb").read())
            base64_string = jpgtxt.decode()
            f["image"] = base64_string
        return jsonlist

    def sendProviderList(self, client,name):
        providerList = self.database.getContentProviders(name)
        print("{}".format(providerList))
        providerList = self.preSend(providerList)
        buffer = json.dumps(providerList, default=str)
        client.send(buffer.encode()+"\n".encode())

    def sendContentList(self, client,name):
        channelList = self.database.getContents(name)
        print("Content list inviata")
        channelList = self.preSend(channelList)
        buffer = json.dumps(channelList, default=str)
        client.send(buffer.encode()+"\n".encode())

    def getStream(self, client):
        response = {}
        response['status'] = 'success'
        response = json.dumps(response)
        client.send(response.encode()+"\n".encode())

    def stopStream(self, client):
        self.getStream(client)


    #content: {'idContentProvider': 1, 'idContent': 1, 'nameProvider': 'InputProvider1', 'nameContent': 'InputContent1', 'startingTime': datetime.datetime(2017, 6, 21, 16, 40, 56), 'length': datetime.time(2, 0)}
    def recContent(self,client, idContent,name):
        content=self.database.getInfoRec(idContent)
        content['name']=name
        print ("content: {} ".format(content))
        data = self.es.recordContent(content)
        print( bcolors.OKGREEN+"{}".format(data)+bcolors.ENDC)
        datasend = client.send((data+"\n").encode())
       

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size).decode().strip()
                print (data)
                if data:
                    response = json.loads(data)
                    operation = response.get('operation', None)
                    print("operation: " + operation)
                    if operation in 'provider list':
                        name = response.get('name',None)
                        self.sendProviderList(client,name)
                    elif operation in 'channel list':
                        name = response.get('name',None)
                        self.sendContentList(client,name)
                    elif operation in ['get stream', 'get channel', 'remove dlna']:
                        self.getStream(client)
                    elif operation in 'stop channel':
                        self.getStream(client)
                    elif operation in "rec content":
                        idContent=response.get('idContent',None)
                        name=response.get('name',None)
                        if idContent is not None:
                            self.recContent(client,idContent,name)
                        else:
                            message={"status":"no id Content"}
                            client.send(json.dumps(message).encode())
                    else:
                        print("operation not allowed")
                        message={"status":"operation not allowed"}
                        client.send(json.dumps(message).encode())
                else:
                    raise Exception('Client disconnected')
            except Exception as ex:
                traceback.print_exc()
                print("EXCEPTION: {}".format(ex))
            finally:
                client.close()
                break


if __name__ == "__main__":
    if len(sys.argv) == 2:
        config=configparser.ConfigParser()
        config.read(sys.argv[1])
        if ("EdgeAcquirer") in config.sections():
            print(bcolors.OKGREEN+"there is the Edge Acquirer section"+bcolors.ENDC)
            addr=config["EdgeAcquirer"]["ip"]
            port=int(config["EdgeAcquirer"]["port"])
        else: 
            print (bcolors.WARNING+"Error there is no Edge Acquirer Section"+ bcolors.ENDC)
            sys.exit(-1)
        if ("Database") in config.sections():
            print(bcolors.OKGREEN+"There is a Database Section"+bcolors.ENDC)
            ip=config["Database"]["ip"]
            username=config["Database"]["username"]
            password=config["Database"]["password"]
            dbport=int(config["Database"]["port"])
            name=config["Database"]["name"]
        else:
            print(bcolors.FAIL+" ERROR There is no Database Section"+bcolors.ENDC)
            sys.exit(-1)
        if ("EdgeStorage") in config.sections():
            print(bcolors.OKGREEN+"There is an Edge Storage Section"+bcolors.ENDC)
            ipStorage = config['EdgeStorage']['ip']
            portStorage = int(config ['EdgeStorage']['port'])
        else:
            print(bcolors.FAIL+" ERROR There is no Storage Section"+bcolors.ENDC)
            ipStorage = "0"
            portStorage = 0
        print("Edge Acquirer starts on {} port {}".format(addr,port))
        print("Database url {}:{} and name {} username {} password {}".format(ip,dbport,name,username,password))
        print("Edge Storage on {}:{}".format(ipStorage,portStorage))
        EdgeAcquirer(addr,port,name,ip,dbport,username,password,ipStorage,portStorage).listen()
    else:
        print ("usage {} configfile".format(sys.argv[0]))