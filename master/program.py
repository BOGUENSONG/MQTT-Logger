import paho.mqtt.client as mqtt
import argparse
import time
import json, zipfile
import tempfile
import sys, os

#------------------------------------------------
# definition KFPKG CLASS()
#------------------------------------------------

class KFPKG():
    def __init__(self):
        self.fileInfo = {"version": "0.1.0", "files" : [] }
        self.filePath = {}
        self.burnAddr = []
    
    def addFile(self, addr, path, prefix=False):
        if not os.path.exists(path):
            raise ValueError(tr("FilePathError"))
        if addr in self.burnAddr:
            raise ValueError(tr("Burn addr duplicate") + ":0x%06x" %(addr))

        f = {}
        f_name = os.path.split(path)[1]
        f["address"] = addr
        f["bin"] = f_name
        f["sha256Prefix"] = prefix
        self.fileInfo["files"].append(f)
        self.filePath[f_name] = path
        self.burnAddr.append(addr)

    def listDumps(self):
        kfpkg_json = json.dumps(self.fileInfo, indent=4)
        return kfpkg_json

    def listDump(self, path):
        with open(path, "w") as f:
            f.write(json.dumps(self.fileInfo, indent=4))

    def listLoads(self, kfpkgJson):
        self.fileInfo = json.loads(kfpkgJson)

    def listLload(self, path):
        with open(path) as f:
            self.fileInfo = json.load(f)

    def save(self, path):
        listName = os.path.join(tempfile.gettempdir(), "kflash_gui_tmp_list.json")
        self.listDump(listName)
        try:
            with zipfile.ZipFile(path, "w") as zip:
                for name,path in self.filePath.items():
                    zip.write(path, arcname=name, compress_type=zipfile.ZIP_DEFLATED)
                zip.write(listName, arcname="flash-list.json", compress_type=zipfile.ZIP_DEFLATED)
                zip.close()
        except Exception as e:
            os.remove(listName)
            raise e
        os.remove(listName)
#--------------------------- end definition KFPKG class ---------------------------------


#-- start bin to kfpkg 
def packFileProcess(fileSaveName):
    # generate flash-list.json
    kfpkg = KFPKG()
    addr = int(address,16)
    path =  filename
    prefix = True
    kfpkg.addFile(addr, path, prefix)
    kfpkg.save(fileSaveName)
    print("\033[32m" + "[Info]" + "\033[0m" + " Save kfpkg success")
#-- end bin to kfpkg

# if server connect, call this function
def on_connect(client, userdata, flags, rc):
    print("server connect success")
# if publish, call this function
def on_publish(client, userdata, mid):
    print("\033[32m" +"send success to id= " + deviceID)
    print("\033[0m")

# fileinfo convert to json for mqtt communication
def dict_to_binary(dict_data):
    dump = json.dumps(dict_data)
    binary = ' '.join(format(ord(letter), 'b') for letter in dump)
    return binary

serverIP = 'log-server.local'
serverPort = 1883 

#parameter parse
parser = argparse.ArgumentParser(description='program bin send')
parser.add_argument('--n', required=True, help='ex) --n=id1')
parser.add_argument('--b', required=True, help='ex) --b=output.bin')
parser.add_argument('--A', required=False, help='ex) --A=0x1080', default="0")
args = parser.parse_args()

deviceID = str(args.n)
filename = str(args.b)
address = str(args.A)

#store temp.kfpkg
packFileProcess("temp.kfpkg")

#fileinfo = { "filename" : filename, 'address' : address }
#bininfo = dict_to_binary(fileinfo)

topic1 = "command/" + deviceID + "/nolja/bin"
topic2 = "command/" + deviceID + "/kflash/bit_mic"
topic3 = "command/" + deviceID + "/kflash/dan"
numb = 0
while True:
    print("##### select topic ###############")
    print(" 1. " + topic1)
    print(" 2. " + topic2)
    print(" 3. " + topic3)
    print("##################################")
    print("number : ",end="")
    numb = input()
    print("##################################")
    if (numb is "1"):
        dest = topic1
        break
    elif (numb is "2"):
        dest = topic2
        break
    elif (numb is "3"):
        dest = topic3
        break
    else:
        print("\nWrong Number Choose another one\n")
        

client = mqtt.Client() #produce client
client.on_connect = on_connect #call back func
client.on_publish = on_publish #call back func
client.connect('log-server.local',1883) # connect to server
if (dest == topic1):
    f = open(filename,'rb')
elif ((dest == topic2) or (dest == topic3)):
    f = open("temp.kfpkg",'rb')
data = f.read()
f.close()
client.publish(dest,filename,qos=0)
client.publish(dest,data,qos=1)
client.disconnect() #discconect server
