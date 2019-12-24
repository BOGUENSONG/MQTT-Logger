import paho.mqtt.client as mqtt
import datetime



def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connect")
    else:
        print("Bad connection")

def on_message(client, userdata, msg):
    logmsg = str(msg.payload.decode('utf-8'))

    idName = msg.topic.replace("log/","")
    filename = "/app/usb/" + logmsg[0:10]+ "_" + idName + ".txt"
    logfile = open(filename,'a')
    logfile.write(logmsg + "\n")
    logfile.close()

    print(logmsg)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('log-server.local', 1883)
client.subscribe('log/#',1)
client.loop_forever()
