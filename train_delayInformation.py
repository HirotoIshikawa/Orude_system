# -*- coding: utf-8 -*-
#Train Delay System on OrudeSystem　04/13 2017
import json, config
import requests
from requests_oauthlib import OAuth1Session
import urllib2
import bs4
from datetime import datetime
#Twitter_apikey
CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS)

alert_count = 0
#LINEnotify用
LINE_ACCESS_TOKEN = "***********"
url = "https://api.twitter.com/1.1/statuses/update.json"
now = datetime.now()

#スクレイプ用urlと表示用短縮url
URL_Odakyu_odawara = 'https://transit.yahoo.co.jp/traininfo/detail/110/0/'
short_Odakyu_odawara = 'https://goo.gl/hac6g4'
URL_Odakyu_enoshima = 'https://transit.yahoo.co.jp/traininfo/detail/109/0/'
short_Odakyu_enoshia = 'https://goo.gl/V3BCmU'
URL_Dento = 'https://transit.yahoo.co.jp/traininfo/detail/114/0/'
short_Dento = 'https://goo.gl/IKsFse'
URL_Yokohama = 'https://transit.yahoo.co.jp/traininfo/detail/31/0/'
short_Yokohama = 'https://goo.gl/9F3WHg'

#スクレイプ
html_Odakyu_odawara = urllib2.urlopen(URL_Odakyu_odawara).read()
html_Odakyu_enoshima = urllib2.urlopen(URL_Odakyu_enoshima).read()
html_Dento = urllib2.urlopen(URL_Dento).read()
html_Yokohama = urllib2.urlopen(URL_Yokohama).read()

soup_Odakyu_odawara = bs4.BeautifulSoup(html_Odakyu_odawara, 'lxml')
soup_Odakyu_enoshima = bs4.BeautifulSoup(html_Odakyu_enoshima, 'lxml')
soup_Dento = bs4.BeautifulSoup(html_Dento, 'lxml')
soup_Yokohama = bs4.BeautifulSoup(html_Yokohama, 'lxml')


#スクレイプ結果判定とメッセージ作成
#span発見時に遅延情報
#Line用とTwitter用のメッセージを作成
if soup_Odakyu_odawara.find('span', class_='icnNormalLarge') is None:
	text_Odakyu_odawara = '小田急: 遅延\n↳' + short_Odakyu_odawara + '\n'
	Line_text_Odakyu_odawara = '小田急線 '
	alert_count = alert_count + 1
else:
	text_Odakyu_odawara = '小田急: 平常運転\n'
	Line_text_Odakyu_odawara =''

if soup_Dento.find('span', class_='icnNormalLarge') is None:
	text_Dento = '田都: 遅延\n↳' + short_Dento + '\n'
	Line_text_Dento = '田園都市線 '
	alert_count = alert_count + 1
else:
	text_Dento = '田都: 平常運転\n'
	Line_text_Dento = ''

if soup_Yokohama.find('span', class_='icnNormalLarge') is None:
	text_Yokohama = '横浜線: 遅延\n↳' + short_Yokohama + '\n'
	Line_text_Yokohama = '横浜線 '
	alert_count = alert_count + 1
else:
	text_Yokohama = '横浜線: 平常運転\n'
	Line_text_Yokohama = ''

if alert_count == 0:
	alert_message = '遅延してる路線はないよ～! ￣O￣)ノｵﾊｰ\n'
else:
	alert_message = '遅延してますね～ヾ(ﾟ０ﾟ*)ノ\n'
	line_message = "今朝は" + Line_text_Odakyu_odawara + Line_text_Dento + Line_text_Yokohama + "が遅延してます。気をつけて来てね〜ヾ(´ε｀*)ゝ"
	payload = {'message':line_message}
	headers = {'Authorization':'Bearer ' + LINE_ACCESS_TOKEN}
	r = requests.post('https://notify-api.line.me/api/notify', data=payload, headers=headers)

#twitterへポスト
message = 'さがキャン周辺の路線情報〜！\n' + alert_message + text_Odakyu_odawara + text_Dento + text_Yokohama + now.strftime("%H:%M:%S")
print(message)
params = {"status":message}
req = twitter.post(url, params = params)
