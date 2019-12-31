import serial
import paho.mqtt.client as mqtt
import datetime
import pytz
import time
import argparse
import RPi.GPIO as GPIO
import time
import binascii
import sys
from PyCRC.CRCCCITT import CRCCCITT

# parameter parse###########################################################

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

##################### flag for download bin ###############################
progress = 0
fname = 'unknown'
###########################################################################

#server address & port , mqtt default port 1883
broker_address = str(address[0])
broker_port = int(address[1])

#serial communication config (device,bitrate)
ser = serial.Serial(port=device,
        baudrate=bitrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=2)

# on_connect callback function
def on_connect(client, userdata, flags, rc):
    print("server connect")

# on_message callback function
def on_message(client, userdata, msg):
    topic = msg.topic
    topic_head = 'command/' + idnum
    if (topic == topic_head  + "/reboot"): # if message was received to reboot, exec this
        resetDevice() 
    elif (topic == topic_head + "/program/bin"): # if message was received to bin, exec this
        global progress #for change global variable flag( stop ser.readline() in while)
        global fname #for change global variable filename
        progress = 1 #change value 0 -> 1

        if (msg.qos == 0):
            fname = msg.payload # filename save
        else:
            print'== canceling ser.readline() 3sec.... =='
            time.sleep(3) #wait readline state change 3sec
            if (fname == 'unknown'): #if filename didn't save, don't exec sendProgram
                progress = 0
                print("file name down error")
            else: # if filename receive successfull, then exec sendProgram
                data = msg.payload
                sendProgram(data,fname)
                progress = 0 #if sendProgram is finished, then progress value change 1->0
                print'---bin download process Complete---'

    else:
        print("unknown topic")

##################################################################################################
# reset function def
def resetDevice():
    print("reset start")
    GPIO.setmode(GPIO.BCM) # GPIO set BCM mode
    GPIO.setup(26,GPIO.IN,pull_up_down=GPIO.PUD_UP) # GPIO number , in-out mode , pulldown set
    GPIO.setup(26,GPIO.OUT,initial=0) 
    time.sleep(1) #1 sec stop
    GPIO.output(26,1) # GPIO number, 0 or 1 : output signal 1 or 0
    GPIO.cleanup() # all GPIO to input mode
    print("reset finish ")

# program send method
def sendProgram(data,filename):

    print("file download...")
    print("file name >>> " + filename)

    f = open(filename,'wb')
    f.write(data)
    f.close()
    print("download complete. serial communication start")
    
    GPIO.setmode(GPIO.BCM) # GPIO set BCM mode
    GPIO.setup(21,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(21,GPIO.OUT,initial=0)
    
    resetDevice()
    time.sleep(3)
    sendData(filename)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.cleanup()

    
# Date send method
def sendData(filename):

    try:
        f = open(filename,'rb')
        image = f.read()
        f.seek(0)

    except IOError:
        print 'cannot open file'

    resp = sendMassErase(ser)
    print 'erasing...'
    
    addr= 0
    written = 0
    printed = 0

    while True:
        block = f.read(256)
        if block == '':
            break
        resp = sendDataBlock(ser,addr,block)
        if resp == '':
            print 'communication Error'
            sys.exit(3)

        written += len(block)
        addr += len(block)

        print '\r'
        while printed > 0:
            print ''
            printed -= 1
        print '\r'

        p = 'Flashing: %.2f %% (%u / %u)'% (written *100. / len(image), written, len(image))
        printed = len(p)
        print p,
        sys.stdout.flush()

    print ''

    myCrc = CRCCCITT(version='FFFF').calculate(image)
    resp = sendCRCCheck(ser, 0, len(image))
    devCrc = ord(resp[5]) + (ord(resp[6]) << 8)
    #print 'CRC:0x%04x expected, but 0x%04x' % (myCrc, devCrc)
    resp = sendReset(ser)
    f.close()

    if myCrc == devCrc:
        print "Integrity check passed."
    else:
        print "integrity check failed"

# Formatting function for log time format
def clock():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    
    return datetime.datetime.now().replace(tzinfo=pytz.utc).isoformat()

###################################################################################################
#                                                                                                 #
# for transffer                                                                                   #
#                                                                                                 #
###################################################################################################
def sendMessage(ser, data, waitTime):
    msg = bytearray(b'\x80')
    msg.append((len(data) >> 0) & 0xFF)
    msg.append((len(data) >> 8) & 0xFF)
    msg += data
    crc = CRCCCITT(version='FFFF').calculate(str(data))
    msg.append((crc >> 0) & 0xFF)
    msg.append((crc >> 8) & 0xFF)
    ser.write(msg)
    #print 'sendMessage>', ' '.join("%02x" % b for b in msg)
    time.sleep(waitTime)
    resp = []
    while True:
        r = ser.read(1)
        if r == '':
            break
        resp += r
        if ser.in_waiting == 0:
            break  
    return resp

def sendMassErase(ser):
    msg = bytearray(b'\x15')
    resp = sendMessage(ser, msg, 1)
    return resp

def sendDataBlock(ser, addr, data):
    msg = bytearray(b'\x10')
    msg.append((addr >> 0) & 0xFF)
    msg.append((addr >> 8) & 0xFF)
    msg.append((addr >> 16) & 0xFF)
    msg += data
    resp = sendMessage(ser, msg, 0.1)
    if len(resp) == 8 and resp[0] == '\x00' and resp[1] == '\x80' and resp[2] == '\x02' and resp[3] == '\x00' and resp[4] == '\x3b' and resp[5] == '\x00' and resp[6] == '\x60' and resp[7] == '\xc4':
        return resp
    else:
        return ''

def sendCRCCheck(ser, addr, length):
    msg = bytearray(b'\x16')
    msg.append((addr >> 0 ) & 0xFF)
    msg.append((addr >> 8 ) & 0xFF)
    msg.append((addr >> 16) & 0xFF)
    msg.append((length >> 0 ) & 0xFF)
    msg.append((length >> 8 ) & 0xFF)
    msg.append((length >> 16) & 0xFF)
    resp = sendMessage(ser,msg,1)
    return resp

def sendReset(ser):
    msg = bytearray(b'\x17')
    resp = sendMessage(ser,msg,0)
    return resp

##################################################################################################
            # Program Main #
#################################################################################################
client = mqtt.Client() #client config
client.on_connect = on_connect # on_connect callback function config
client.on_message = on_message # on_message callback function config
client.connect(host=broker_address, port=broker_port) #server conncet
client.subscribe('command/' + idnum + '/reboot',1) #subscribe for reset
client.subscribe('command/' + idnum + '/program/bin',1) #suscribe for bin file
client.loop_start() #loop start
while 1:
    if (progress == 0):
        logline = ser.readline() #read log from device when progress is not doing
        timestamp = clock()
        log = timestamp  + " / " + logline
        print log,
        client.publish("log/" + idnum,log)
    else:
        logline = "progress is busy now "
