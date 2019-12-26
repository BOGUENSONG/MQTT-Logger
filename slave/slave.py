import serial
import paho.mqtt.client as mqtt
import datetime
import pytz
import time
import argparse

#server address & port , mqtt default port 1883
broker_address ='log-server.local'
broker_port = 1883

# serial communication config (device,bitrate)
ser = serial.Serial('/dev/ttyACM0',115200) 

# on_connect callback function
def on_connect(client, userdata, flags, rc):
    print("연결이 완료되었습니다")

# Formatting function for log time format
def clock():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


client = mqtt.Client() #client config
client.on_connect = on_connect # on_connect callback function config

client.connect(host=broker_address, port=broker_port) #server conncet

client.loop_start() #loop start
while 1: 
    logline = ser.readline() #read log from device
    timestamp = clock() # get present time
    log = timestamp + " / "+ str(logline) # log message fotmat [ timestamp / logmsg]
    print(log) # print for debug
    client.publish("log/id1",log) # publish to "topic", log
    

