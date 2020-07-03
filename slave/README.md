# SLAVE
------------------------------------------
### 1. kflash.py
 * slave.py에서 실행하는 프로그램으로, kendryte에서 직접 관리해주는 파일을 사용한다. 

#### [>> Click <<](https://github.com/kendryte/kflash.py)
------------------------------------------
### 2. slave.py


[ 바이너리 파일 flash, 장비 리셋등 gpio 혹은 serial 통신으로 연결된 장비 관리 프로그램 ]

 - 라이브러리 : mqtt, serial, RPi.GPIO, pytz
 - 실행환경 : 라즈베리파이, python2
 - 파라미터 : --s 서버주소, --p 장비위치, --n 장비이름
```
 예) $ python slave.py --s=log-server.local:1883 --p=/dev/ttyUSB0 --n=id1
```
------------------------------------------  
#### **프로그램 동작방식**

 main
1. ser.readline()함수로 시리얼포트로 들어오는 내용을 가져온다.
2. 내용에 timestamp를 붙여 로그서버로 전송한다. 

 interrupt
1. 특정 토픽을 subscribe를 하다 어떠한 정보가 들어오면, 콜백함수인 on_message 함수로 이동한다.

2. on message()  
ser.readline()을 멈추게 하기위해 flag인 progress를 1로 올린다.   
토픽의 종류, 받은 메세지, qos를 분석하여 해당하는 함수를 실행한다.
> ##### command/장비이름/reboot  
> ```
> resetDevice() 함수를 실행
> ```
> ##### command/장비이름/nolja/bin  
> ##### command/장비이름/kflash/bit_mic  
> ##### command/장비이름/kflash/dan  
> ```
> 1. (공통) qos가 0인 토픽에서 바이너리 파일명을 저장한다.
> 2. qos가 1인 토픽에서온 데이터(bin raw file) 를 임시로 디스크의 현재 위치에 저장한다.
> 3. 저장한 데이터를 이용해 장비에 flashing한다.
>>> sendProgram : nolja.py 기반으로 제작. resetDevice() 후 sendData()를 이용해 bin파일 flashing
>>> sendCamProgram : run_command 사용, kfalsh.py를 이용해 bin파일 flashing
> ```
  각 함수 수행 후 filename, progress를 초기화하여 readline()을 재시작한다.

------------------------------------------
