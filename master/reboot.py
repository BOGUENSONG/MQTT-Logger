import paho.mqtt.client as mqtt
import datetime
import argparse

#parameter parse
parser = argparse.ArgumentParser(description='device reset program')
parser.add_argument('--n', required=True, help='ex) --n=id1')
args = parser.parse_args()

deviceID = str(args.n)

# if server connect , call this function
def on_connect(client, userdata, flags, rc):
    print("connect success")
# if publish, call this function
def on_publish(client, userdata, mid):
    print("send success to topic")

client = mqtt.Client() #produce client
client.on_connect = on_connect # callback function config
client.on_publish = on_publish # callback function config
client.connect('log-server.local', 1883) #connect server
 
client.publish("command/" + deviceID + "/reboot", "go reset device") #request reset

client.disconnect() #disconnect from server
