# MASTER
------------------------------------------
### 1. master.py  

[ 특정 토픽으로 부터 오는 로그메세지를 읽어 텍스트파일로 저장 ]

 - 라이브러리 : mqtt
 - 파라미터 : --l 텍스트 파일 저장할 위치
```
 예) : $ python3 master.py --l=/app/usb
```
------------------------------------------
### 2. program.py

[ 바이너리 파일을 특정토픽의 특정장비로 전송하여 flashing ]

 - 라이브러리 : mqtt
 - 파라미터 : --n 장비id --b 바이너리 파일명
```
 예) $ python3 program.py --n=id1 --b=dvp2sdcard_dev.bin
     
*2020년 2월 5일 현재 구현된 토픽 3개

### select topic ######
1. command/id1/nolja/bin
2. command/id1/kflash/bit_mic
3. command/id1/kflash/dan
######################
number : 1
```
------------------------------------------
### 3. reboot.py
[ 특정토픽으로 reset 명령을 전달하여 장비 리셋 ]
 - 라이브러리 : mqtt
 - 파라미터 : --n 장비id
```
 예) & python3 reboot.py --n=id1
```
