import serial
import paho.mqtt.client as mqtt
import datetime
import pytz
import time

broker_address ='log-server.local'
broker_port = 1883

ser = serial.Serial('/dev/ttyACM0',115200)
def on_connect(client, userdata, flags, rc):
    print("연결이 완료되었습니다")
def clock():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()
#def on_publish(client, userdata, mid)
  #  print()


client = mqtt.Client()
client.on_connect = on_connect
#client.on_publish = on_publish

client.connect(host=broker_address, port=broker_port)
client.loop_start()
while 1:
    logline = ser.readline()
    timestamp = clock()
    log = timestamp + " / "+ str(logline)
    print(log)
    client.publish("log/id1",log)
    

