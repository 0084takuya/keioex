#encoding:utf-8
import sys
import urllib.request, urllib.error
import json
import open_jtalk
import subprocess

url = 'https://rti-giken.jp/fhc/api/train_tetsudo/delay.json'
resp = urllib.request.urlopen(url=url).read().decode('utf-8')

subprocess.call("aplay train-bell1.wav", shell=True)

# 読み込んだJSONデータをディクショナリ型に変換
resp = json.loads(resp)
open_jtalk.talk('鉄道情報です')
for res in resp:
        open_jtalk.talk(res['company'] + ' ' + res['name'])
open_jtalk.talk('以上は現在遅延しているかもしれません 詳しい運行情報は自分で調べてください')
