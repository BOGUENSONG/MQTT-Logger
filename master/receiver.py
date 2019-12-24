import paho.mqtt.client as mqtt
import datetime


# 서버에 연결 되었을 때 실행되는 함수
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connect")
    else:
        print("Bad connection")

# message가 도착했을 때 실행되는 함수
def on_message(client, userdata, msg):
    logmsg = str(msg.payload.decode('utf-8')) #로그메시지
    folderName = "/app/usb/"
    idName = msg.topic.replace("log/","") # 메시지 보낸 장치의 토픽id
    filename = folderName + logmsg[0:10]+ "_" + idName + ".txt" # 저장할 파일위치/YYYY-MM-DD_id#.txt의 형식 
    logfile = open(filename,'a')
    logfile.write(logmsg + "\n")
    logfile.close()

    print(logmsg) #화면에도 로그메세지 출력


client = mqtt.Client() #클라이언트 설정
client.on_connect = on_connect #콜백함수 설정 (연결완료시)
client.on_message = on_message #콜백함수 설정 (메시지도착시)

client.connect('log-server.local', 1883) # 서버에 연결
client.subscribe('log/#',1) # 토픽명이 log/로 시작하는모든 것들을 구독한다.
client.loop_forever() #계속 반복한다.
