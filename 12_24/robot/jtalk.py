# coding:utf-8

import subprocess

import baserobot as br

class JTalkController(br.Controller):
    def __init__(self, cmd_queue):
        super().__init__(cmd_queue)
    
    def handle_command(self):
        while True:
            cmd = self.cmd_queue.get()
            cmd_shell = ['aplay', cmd]
            subprocess.call(cmd_shell)

