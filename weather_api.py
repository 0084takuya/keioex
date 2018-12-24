#encoding:utf-8

import sys
import json
import urllib.request, urllib.error
import open_jtalk

try: citycode = sys.argv[1]
except: citycode = '140010' #デフォルト地域

url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=%s'%citycode
resp = urllib.request.urlopen(url=url).read().decode('utf-8')

# 読み込んだJSONデータをディクショナリ型に変換
resp = json.loads(resp)
#print ('**************************')
#print (resp['title'])
#print ('**************************')
#print (resp['description']['text'])

for forecast in resp['forecasts']:
    #print ('**************************')
    #print (forecast['dateLabel']+'('+forecast['date']+')')
    #print (forecast['telop'])
    #print ('**************************')
    open_jtalk.talk('ここの' + forecast['dateLabel'] + 'の天気は' + forecast['telop'] + 'です')
