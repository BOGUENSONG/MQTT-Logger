import paho.mqtt.client as mqtt
import argparse

serverIP = 'log-server.local'
serverPort = 1883 

#parameter parse
parser = argparse.ArgumentParser(description='program bin send')
parser.add_argument('--n', required=True, help='ex) --n=id1')
parser.add_argument('--b', required=True, help='ex) --b=output.bin')
args = parser.parse_args()

deviceID = str(args.n)
filename = str(args.b)
dest = "command/" + deviceID + "/program/bin"
message = "send " + filename


# if server connect, call this function
def on_connect(client, userdata, flags, rc):
    print("server connect success")
# if publish, call this function
def on_publish(client, userdata, mid):
    print("send success to id= " + deviceID)


client = mqtt.Client() #produce client
client.on_connect = on_connect #call back func
client.on_publish = on_publish #call back func
client.connect('log-server.local',1883) # connect to server

client.publish(dest,message) # send message to topic

client.disconnect() #discconect server


