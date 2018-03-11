#!/usr/bin/env python
# -*- coding: utf-8 -*-

#2017/04/01 ver1
#2017/09/25 ver2
 
import io
import fcntl
import time
import struct
import urllib2
import json
import requests
import datetime
import random

#LINEnotify用
LINE_ACCESS_TOKEN = "*********"

#センサーの制御
class I2CBus:
    # ioctl 用 (Linux の i2c-dev.h の定義から引用)
    I2C_SLAVE =      0x0703
 
    def __init__(self, bus):
        self.wh = io.open('/dev/i2c-' + str(bus), mode='wb', buffering=0)
        self.rh = io.open('/dev/i2c-' + str(bus), mode='rb', buffering=0)
 
    def write(self, dev_addr, reg_addr, param=None):
        fcntl.ioctl(self.wh, self.I2C_SLAVE, dev_addr)
        data=bytearray()
        data.append(reg_addr)
        if type(param) is list:
            data.extend(param)
        elif not param is None:
            data.append(param)
        self.wh.write(data)
 
    def read(self, dev_addr, count, reg_addr=None):
        fcntl.ioctl(self.wh, self.I2C_SLAVE, dev_addr)
        fcntl.ioctl(self.rh, self.I2C_SLAVE, dev_addr)
 
        if not reg_addr is None:
            self.wh.write(bytearray([reg_addr]))
 
        return self.rh.read(count)
 
class TSL2561:
    DEV_ADDR            = 0x39 # 7bit
 
    REG_CTRL            = 0x80
    REG_TIMING          = 0x81
    REG_DATA            = 0x9B
    REG_ID              = 0x8A
 
    INTEG_13MS          = 0x00
    INTEG_101MS         = 0x01
    INTEG_402MS         = 0x02
 
    GAIN_1X             = 0x00
    GAIN_16X            = 0x10
 
    POWER_ON            = 0x03
    POWER_OFF           = 0x00
 
    gain = GAIN_1X
    integ = INTEG_402MS
 
    def __init__(self, bus, dev_addr=DEV_ADDR):
        self.bus = bus
        self.dev_addr = dev_addr
        self.i2cbus = I2CBus(bus)
 
    def enable(self):
        self.i2cbus.write(self.dev_addr, self.REG_CTRL, self.POWER_ON)
 
    def disable(self):
        self.i2cbus.write(self.dev_addr, self.REG_CTRL, self.POWER_OFF)
 
    def set_timing(self):
        value = self.gain | self.integ
        self.i2cbus.write(self.dev_addr, self.REG_TIMING, value)
 
    def set_gain(self, gain):
        self.gain = gain
 
    def set_integ(self, integ):
        self.integ = integ
 
    def wait(self):
        if self.integ == self.INTEG_13MS:
            time.sleep(0.14)
        if self.integ == self.INTEG_101MS:
            time.sleep(0.102)
        if self.integ == self.INTEG_402MS:
            time.sleep(0.403)
 
    def get_lux(self):
        self.set_timing()
        self.enable()
        self.wait()
 
        value = self.i2cbus.read(self.dev_addr, 5, self.REG_DATA)
 
        temp = struct.unpack('>H', bytes(value[0:2]))[0]
 
        ch0 = float(struct.unpack('<H', bytes(value[1:3]))[0])
        ch1 = float(struct.unpack('<H', bytes(value[3:5]))[0])

        if ch0 <= 0:
            ch0 = 0.01
 
        self.disable()
 
        if (self.gain == self.GAIN_1X):
            ch0 *=16
            ch1 *=16
 
        if (self.integ == self.INTEG_13MS):
            ch0 *= 322.0/11
            ch1 *= 322.0/11
        elif (self.integ == self.INTEG_101MS):
            ch0 *= 322.0/81
            ch1 *= 322.0/81
 
        if (ch1/ch0) <= 0.52:
            return 0.0304*ch0 - 0.062*ch0*((ch1/ch0)**1.4)
        elif (ch1/ch0) <= 0.65:
            return 0.0224*ch0 - 0.031*ch1
        elif (ch1/ch0) <= 0.80:
            return 0.0128*ch0 - 0.0153*ch1
        elif (ch1/ch0) <= 1.30:
            return 0.00146*ch0 - 0.00112*ch1;
        else:
            return 0;

#Lineへの送信
def post_LINE_notify(line_text):
    payload = {'message':line_text}
    headers = {'Authorization':'Bearer ' + LINE_ACCESS_TOKEN}
    r = requests.post('https://notify-api.line.me/api/notify', data=payload, headers=headers)
    print(r)

#時間帯の判定    
def timetable():
    now_time = datetime.datetime.now()
    set_time = datetime.time(now_time.hour,now_time.minute)

    if datetime.time(0,0) <= set_time and datetime.time(8,59) >= set_time:
        return "朝"
    elif datetime.time(9,0) <= set_time and datetime.time(10,29) >= set_time:
        return "一限目"
    elif datetime.time(10,30) <= set_time and datetime.time(10,59) >= set_time:
        return "礼拝時間"
    elif datetime.time(11,0) <= set_time and datetime.time(12,29) >= set_time:
        return "２限目"
    elif datetime.time(12,30) <= set_time and datetime.time(13,19) >= set_time:
        return "昼休み"
    elif datetime.time(13,20) <= set_time and datetime.time(14,49) >= set_time:
        return "３限目"
    elif datetime.time(15,5) <= set_time and datetime.time(16,34) >= set_time:
        return "４限目"
    elif datetime.time(16,50) <= set_time and datetime.time(18,19) >= set_time:
        return "５限目"
    elif datetime.time(18,20) <= set_time and datetime.time(23,59) >= set_time:
        return "放課後"
    else:
        return "休み時間"

#顔文字の設定hello
def hello_kaomoji():
	hello_num = random.randint(1,10)
	if hello_num == 1:
		return "ﾜｰｲε=ヾ(*・∀・)/"
	elif hello_num == 2:
		return "(*´罒`*)ﾆﾋﾋ"
	elif hello_num == 3:
		return "(Ο－Ο―)ｷﾘｯｯ!!"
	elif hello_num == 4:
		return "(*`▽´*)ｳﾋｮﾋｮ"
	elif hello_num == 5:
		return "U｡･x･)ﾉ ﾁﾜﾝ!"
	elif hello_num == 6:
		return "(*^･ｪ･)ﾉ ｺﾝﾁｬ♪"
	elif hello_num == 7:
		return "( ´_ゝ`)ﾉﾎﾞﾝｼﾞｭｰﾙ♪"
	elif hello_num == 8:
		return "o( ´_ゝ｀)ﾉｱﾆｮﾊｾﾖ♪"
	elif hello_num == 9:
		return "(/*^^)/ﾊｯﾛ-!!"
	elif hello_num == 10:
		return "(oﾟ□ﾟ)oｺﾝﾆﾁﾜｧｱ!!"
	else:
		return "(￣ー￣)"

#解錠メッセージ
def hello_message():
	hello_mes = random.randint(1,6)
	if hello_mes == 1:
		return "部室開いたよっ！"
	elif hello_mes == 2:
		return "部室が開いてしまったぁ"
	elif hello_mes == 3:
		return "封印されし扉がぁぁ（あいたよ）"
	elif hello_mes == 4:
		return "部室開いたンゴ"
	elif hello_mes == 5:
		return "部室オープン!!"
	elif hello_mes == 6:
		return "開くンゴ開くンゴ"
	else:
		return "部室開いたよ！"
#施錠メッセージ
def goodbye_message():
	goodbye = random.randint(1,5)
	if goodbye == 1:
		return "部室が閉まりました〜"
	elif goodbye == 2:
		return "部室閉まりマース"
	elif goodbye == 3:
		return "閉まるンゴ閉まるンゴ"
	elif goodbye == 4:
		return "部室close"
	elif goodbye == 5:
		return "さらばだ！閉まりました"
	else:
		return "goodbye"

#顔文字の設定goodbye
def goodbye_kaomoji():
	goodbye_num = random.randint(1,10)
	if goodbye_num == 1:
		return "ヾ(*'-'*)ﾏﾀﾈｰ♪"
	elif goodbye_num == 2:
		return "･△･)ﾉ ﾊﾞｲﾊﾞｲ"
	elif goodbye_num == 3:
		return "ヾ( ´ー｀)ﾉ~ばーい"
	elif goodbye_num == 4:
		return "(*ﾟ▽ﾟ)ﾉbye"
	elif goodbye_num == 5:
		return "ﾏﾀﾈｯ(^ｰ^)ﾉ"
	elif goodbye_num == 6:
		return "ｲﾔｧ～ヽ(´Д｀ヽ)"
	elif goodbye_num == 7:
		return "(/´Д｀)/ｲﾔｧ～"
	elif goodbye_num == 8:
		return "(ﾉ_･､)ｼｸｼｸ"
	elif goodbye_num == 9:
		return "(=ﾟ∇ﾟ)ﾎﾞｰ"
	elif goodbye_num == 10:
		return "(*ﾟρﾟ)byebye"
	else:
		return "ヾ(ｰｰ )ｫｨ"

I2C_BUS = 0x1 # Raspberry Pi

tsl2561 = TSL2561(I2C_BUS)
message = ""
line_message = ""
#初期状態の設定
lux = tsl2561.get_lux()

if lux > 13:
    people = True
elif lux < 13:
    people = False

#実行部
while True:
    date = datetime.datetime.now()
    if  datetime.time(date.hour,date.minute) == datetime.time(21,30):
	end = "end" + date.strftime("%Y/%m/%d %H:%M:%S")
	#print(end)
        break
    lux = tsl2561.get_lux()
    if people == False:
        if lux > 13.0:
            line_message = hello_message() + "                     　"+hello_kaomoji()+" ["+timetable()+"]"
            post_LINE_notify(line_message)
            people = True
            time.sleep(15)
        else:
            time.sleep(15)
            continue
    elif people == True:
        if lux < 13.0:
            line_message = goodbye_message() + "              　　　"+goodbye_kaomoji()+" ["+timetable()+"]"
            post_LINE_notify(line_message)
            people = False
            time.sleep(15)
        else:
            time.sleep(15)
            continue
    else:
        time.sleep(15)
        continue
