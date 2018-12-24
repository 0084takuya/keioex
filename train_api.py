#encoding:utf-8
import sys
import urllib.request, urllib.error
import json

url = 'https://rti-giken.jp/fhc/api/train_tetsudo/delay.json'
resp = urllib.request.urlopen(url=url).read().decode('utf-8')

# 読み込んだJSONデータをディクショナリ型に変換
resp = json.loads(resp)
for res in resp:
        print(res['company'] + ' ' + res['name'] + 'は現在遅延しています。')
