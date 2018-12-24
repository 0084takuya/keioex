# coding: utf-8
import os

class openjtalk:
    def __init__(self):
        self.dic = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
        self.htsvoice = "MMDAgent_Example-1.6/Voice/mei/mei_normal.htsvoice"
        self.speed = 1.0
    def speak(self, text):
        command =  "echo '{0}'".format(text)
        command += " | open_jtalk -x {0} -m {1} -r {2} -ow /dev/stdout".format(self.dic, self.htsvoice, self.speed)
        command += " | aplay"
        os.system(command)

def talk(t):
    talker = openjtalk()
    talker.speed = 0.5
    talker.speak(t)

#talker = openjtalk()
#talker.speed = 0.5
#talker.speak("ねえねえこっちみてよ")

