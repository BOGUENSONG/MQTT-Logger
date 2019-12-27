#!/usr/bin/env python

import sys
import time
import serial
import binascii
from PyCRC.CRCCCITT import CRCCCITT

def sendMessage(ser, data, waitTime):
    msg = bytearray(b'\x80')
    msg.append((len(data) >> 0) & 0xFF)
    msg.append((len(data) >> 8) & 0xFF)
    msg += data
    crc = CRCCCITT(version='FFFF').calculate(str(data))
    msg.append((crc >> 0) & 0xFF)
    msg.append((crc >> 8) & 0xFF)
#    print 'sendMessage>', ' '.join("%02x" % b for b in msg)
    ser.write(msg)
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
#   print 'sendMassErase<', ' '.join("%02x" % ord(b) for b in resp)
   return resp

def sendDataBlock(ser, addr, data):
    msg = bytearray(b'\x10')
    msg.append((addr >> 0) & 0xFF)
    msg.append((addr >> 8) & 0xFF)
    msg.append((addr >> 16) & 0xFF)
    msg += data
    resp = sendMessage(ser, msg, 0.1)
#    print 'sendDataBlock<', ' '.join("%02x" % ord(b) for b in resp)
    if len(resp) == 8 and resp[0] == '\x00' and resp[1] == '\x80' and resp[2] == '\x02' and resp[3] == '\x00' and resp[4] == '\x3b' and resp[5] == '\x00' and resp[6] == '\x60' and resp[7] == '\xc4':
        return resp
    else:
        return ''

def sendCRCCheck(ser, addr, length):
    msg = bytearray(b'\x16')
    msg.append((addr >> 0) & 0xFF)
    msg.append((addr >> 8) & 0xFF)
    msg.append((addr >> 16) & 0xFF)
    msg.append((length >> 0) & 0xFF)
    msg.append((length >> 8) & 0xFF)
    msg.append((length >> 16) & 0xFF)
    resp = sendMessage(ser, msg, 1)
#    print 'sendCRCCheck<', ' '.join("%02x" % ord(b) for b in resp)
    return resp

def sendReset(ser):
    msg = bytearray(b'\x17')
    resp = sendMessage(ser, msg, 0)
#    print 'sendReset<', ' '.join("%02x" % ord(b) for b in resp)
    return resp

def printUsage():
    print ('* Usage: %s {serial port} {binary file}' % sys.argv[0])

print ('Nol.ja flasher version 0.5.2 for Nol.A supported boards.')

if len(sys.argv) != 3:
    printUsage()
    sys.exit(3)

try:
    ser = serial.Serial(
        port=sys.argv[1],
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=2)

except serial.SerialException:
    print >> sys.stderr, '* Cannot open port.'
    printUsage()
    sys.exit(1)

try:
    f = open(sys.argv[2], 'rb')
    image = f.read()
    f.seek(0)

except IOError:
    print >> sys.stderr, '* Cannot open file.'
    printUsage()
    sys.exit(2)


resp = sendMassErase(ser)
print ('Erasing...')

addr = 0
written = 0
printed = 0

while True:
    block = f.read(256)
    if block == '':
        break;
    resp = sendDataBlock(ser, addr, block)
    if resp == '':
        print( sys.stderr, '* Communication Error')
        sys.exit(3)

    written += len(block)
    addr += len(block)

    print ('\r'),
    while printed > 0:
        print(' '),
        printed -= 1
    print ('\r'),

    p = 'Flashing: %.2f %% (%u / %u)' % (written * 100. / len(image), written, len(image))
    printed = len(p)
#    print p
    print (p),
    sys.stdout.flush()

print ('')

myCrc = CRCCCITT(version='FFFF').calculate(image)
resp = sendCRCCheck(ser, 0, len(image))

devCrc = ord(resp[5]) + (ord(resp[6]) << 8)
#print 'CRC:0x%04x expected, but 0x%04x' % (myCrc, devCrc)
resp = sendReset(ser)

ser.close()
f.close()

if myCrc == devCrc:
    print ('Integrity check passed.')
    sys.exit(0)
else:
    print >> sys.stderr, 'Integrity check failed.'
    sys.exit(-1)
