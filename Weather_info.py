#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import io
import fcntl
import time
import struct
import urllib2
import json, config
import requests
from requests_oauthlib import OAuth1Session
import datetime
#TwitterApikey
CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS)

url = "https://api.twitter.com/1.1/statuses/update.json"


def tweet_message(message):
    #print("doing")
    params = {"status" : message}
    req = twitter.post(url, params = params)
    #print(req)

def forecast(i):
    url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=140020'
    date = datetime.datetime.now()
    # 天気データ取得
    # 最初に指定URLのデータ取得
    response = urllib2.urlopen(url)
    # jsonデータ取得
    weather = json.loads(response.read())

    today_weather = weather['forecasts'][i]['telop']
    #tomorrow_weather = weather['forecasts'][1]['telop']

#午前と午後メッセージ
    if i==0:
        status_message = u"オハヨウございます！\n"
    elif i==1:
        status_message = u"コンバンワ〜\n"
#最低気温
    if weather['forecasts'][i]['temperature']['min'] is None:
        today_min_text = u"不明"
    else:
        today_min_text = weather['forecasts'][i]['temperature']['min']['celsius'] + u"°C"
#最高気温

    if weather['forecasts'][i]['temperature']['max'] is None:
        today_max_text = u"不明"
    else:
        today_max_text = weather['forecasts'][i]['temperature']['max']['celsius'] + u"°C"

#雨もしくは雪の場合
    if u'雨' in today_weather or u'雪' in today_weather:
        umbrella_message =u" あっ...!\n 傘を忘れずにー！！"
    else:
        umbrella_message =""

    if weather['forecasts'][i]['temperature']['max'] is None:
        today_temp = 401
    else:
        today_temp = int(weather['forecasts'][i]['temperature']['max']['celsius'])
#メッセージ
    if today_temp == 401:
        weather_message = u""
    elif today_temp <= 7:
        weather_message = u"寒すぎて...\nサム━(((ﾟДﾟДﾟДﾟ)))━ィ！"
    elif today_temp <=10:
        weather_message = u"チョーー寒い１日になりそうです。\n(((( ﾟДﾟ))))ｻﾑｩｰ"
    elif today_temp <=13:
        weather_message = u"寒い１日になりそうです。\n((´д｀)) ﾌﾞﾙﾌﾞﾙ…"
    elif today_temp <=15:
        weather_message = u"寒いけどぉ暖かい日になりそう。はいっ!?\n(￣ー￣)ﾉ"
    elif today_temp <=20:
        weather_message = u"過ごしやすい１日になるでしょう。\n(*´▽｀)ﾉﾉ"
    elif today_temp <= 23:
        weather_message = u"あれ？暖かい？暑いかも!? \n(^ ^；)"
    elif today_temp <= 25:
        weather_message = u"暑い一日になるでしょう。\nι(´Д｀υ)"
    elif today_temp <= 26:
        weather_message = u"暑すぎて死んじゃうかも オーバーヒート注意！\n部室冷やしにきて［´Д`]"
    elif today_temp <= 30:
        weather_message = u"暑すぎだろ！おるで！System動作限界温度 死ぬ可能性大ww\nまいったねorz"
    elif today_temp >= 31:
        weather_message = u"暑すぎて死⊂( ･∀･) 彡"

    forecast_message = status_message + u"さがキャンの"+weather['forecasts'][i]['dateLabel']+u"の天気は、"+ today_weather + u"\n最低気温：" + today_min_text + u"  最高気温：" + today_max_text + "\n" + weather_message + umbrella_message+"\n"+date.strftime("%Y/%m/%d  %H:%M")
    tweet_message(forecast_message)

date = datetime.datetime.now()
#制御系
if datetime.time(date.hour,date.minute) < datetime.time(12,10):
    morning_or_night = 0
    forecast(morning_or_night)
    #print("success")
elif datetime.time(date.hour,date.minute) >datetime.time(12,11):
    morning_or_night = 1
    forecast(morning_or_night)
    #print("e")
else:
    print("error")
