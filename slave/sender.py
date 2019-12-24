import serial
import paho.mqtt.client as mqtt
import datetime
import pytz
import time

#broker (서버)의 주소와 포트번호 MQTT는 1883이 기본이다.
broker_address ='log-server.local'
broker_port = 1883

# 시리얼통신 설정과 bitrate설정
ser = serial.Serial('/dev/ttyACM0',115200) 

# 서버와 연결시 실행되는 함수
def on_connect(client, userdata, flags, rc):
    print("연결이 완료되었습니다")

# 현재 시간을 ISO-8601에 맞추어 반환.
def clock():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


client = mqtt.Client() #클라이언트 설정
client.on_connect = on_connect #connect시 콜백함수 설정

client.connect(host=broker_address, port=broker_port) #서버와 연결
client.loop_start() #반복 시작
while 1: 
    logline = ser.readline() #장치로부터 오는 메시지 (로그)를 읽는다.
    timestamp = clock() #현재 시간을 받는다.
    log = timestamp + " / "+ str(logline) #메시지 모양은 현재시간 / 장치로그 로 설정.
    print(log) # 화면에 로그모양을 출력해준다.
    client.publish("log/id1",log) # log/내 id의 토픽으로 로그를 보낸다.
    

