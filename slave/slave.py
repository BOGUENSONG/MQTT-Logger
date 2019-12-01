import serial
import paho.mqtt.client as mqtt
import datetime
import pytz
import time
import argparse

# parameter parse

parser = argparse.ArgumentParser(description='this program send log to server')
parser.add_argument('--s', required=True, help=' ex) --s=log-server.local:1883')
parser.add_argument('--p', required=True, help=' ex) --p=/dev/ttyACM0')
parser.add_argument('--n', required=True, help=' ex) --n=id1')
parser.add_argument('--b', required=False, default='115200', help=' ex) --b=1024')

args =parser.parse_args()

address = args.s.split(':') #split into  address & port 
device = args.p
bitrate = args.b
idnum = args.n 

#server address & port , mqtt default port 1883
broker_address = str(address[0])
broker_port = int(address[1])

# serial communication config (device,bitrate)
ser = serial.Serial(device,bitrate) 

# on_connect callback function
def on_connect(client, userdata, flags, rc):
    print("연결이 완료되었습니다")
# on_message callback function
def on_message(client, userdata, msg):
    print(msg) #print message
    resetDevice() #reset Device



# Formatting function for log time format
def resetDevice():
    print("리셋하는 함수")

def clock():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


client = mqtt.Client() #client config
client.on_connect = on_connect # on_connect callback function config
client.on_message = on_message # on_message callback function config
client.connect(host=broker_address, port=broker_port) #server conncet

client.loop_start() #loop start
while 1: 
    logline = ser.readline() #read log from device
    timestamp = clock() # get present time
    log = timestamp + " / "+ str(logline) # log message fotmat [ timestamp / logmsg]
    print(log) # print for debug
    client.publish("log/" + idnum,log) # publish to "topic", log
    client.subscribe('command/' + idnum + '/reboot',1)

