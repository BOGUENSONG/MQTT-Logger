import paho.mqtt.client as mqtt
import argparse
import time
import json

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

fileinfo = { "filename" : filename, 'address' : address }
bininfo = dict_to_binary(fileinfo)

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
f = open(filename,'rb')
data = f.read()
f.close()
client.publish(dest,bininfo,qos=0)
client.publish(dest,data,qos=1)
client.disconnect() #discconect server
