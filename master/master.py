import paho.mqtt.client as mqtt
import datetime
import argparse

# if server connect , call this function
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connect")
    else:
        print("Bad connection")

# if on message, call this function
def on_message(client, userdata, msg):
    logmsg = str(msg.payload.decode('utf-8')) # logmessage from topic
    folderName = "/app/usb/" #location for save
    idName = msg.topic.replace("log/","") # message sender id
    filename = folderName + logmsg[0:10]+ "_" + idName + ".txt" # folder/YYYY-MM-DD_id#.txt [saving format]
    logfile = open(filename,'a') # open file
    logfile.write(logmsg + "\n") # write log
    logfile.close() # close file

    print(logmsg) # logmesesage print for debugging


client = mqtt.Client() #client config
client.on_connect = on_connect # callback function config (on_connect)
client.on_message = on_message # callback function config (on_message)

client.connect('log-server.local', 1883) # connect server ('servername', port)
client.subscribe('log/#',1) # subscribe all 'topic#'
client.loop_forever() # loop forever
