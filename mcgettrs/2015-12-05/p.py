import SimpleHTTPServer
import SocketServer
import urlparse
import time

from tcdtestbed.server import *
from dwa import *

class dwap(dwa_pon):
    def __init__(self,ip,initialise=False):
        self.pronto=Pronto(ip)
        if initialise:
             self.pronto.sendcmd('bash /home/tcdonalab2.sh')
        super(dwap,self).__init__()
    def post_primary(self):
        self.pronto.sendcmd('bash /home/tcdonalab2_redpath.sh')
    def post_secondary(self):
        self.pronto.sendcmd('bash /home/tcdonalab2_greenpath.sh')

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POSTx(self):
        self.do_GET()

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))
        param={}
        for key, value in post_data.iteritems():
            value=value[0]
            param[key]=value
        self.do_GET()
        self.hndlr(param)

    def hndlr(self,param):
        print "parameters",param
        if not 'quality' in param:
           print "missing parameters"
           return
        print "Setting up topology"
        print videohost.killProcess("vlc")
        print videohost.killProcess("stream")
        sdncontrol.sendcmd("mysql --user=root -p topology --password=password < delete_flows.sql")
        if 'video1' in param:
           part='1000'
        elif 'video2' in param:
           part='1500'
        elif 'video3' in param:
           part='2000'
        elif 'video4' in param:
           part='2500'
        elif 'video5' in param:
           part='3000'

        if(param['quality']=="4000p"):
           request_BW = 3000000
           dw.set_primary_path()
           qual='100'
        elif(param['quality']=="1080p"):
           request_BW = 2000000
           dw.set_secondary_path()
           qual='66'
        elif(param['quality']=="720p"):
           request_BW = 1000000
           dw.set_primary_path()
           qual='40'

        sdncontrol.sendcmd("mysql --user=root -p topology --password=password < insert_flows.sql")
        stx = 'bash start_streaming.sh TimeScapes_UHD_'+qual+'_cbr.mp4 10.0.0.123 1234 '+part
#        videohost.sendcmd('pwd; whoami')
        videohost.sendcmd(stx)
#        print 'Playing content TimeScapes_UHD_'+qual+'_cbr.mp4 10.0.0.123 1234 '+part
        time.sleep(60)
        print "timedout"


if __name__ == "__main__":

   dw=dwap(ip='10.10.10.11')
   dw.set_wss()
   dw.check_interfaces()
   dw.baseline()
   dw.check_tunability()

   videohost=server('10.10.10.51','ol09','qwerty09', sudo=False)
   sdncontrol=server('127.0.0.1','ubuntu','ubuntu', sudo=False)
#   videohost.sendcmd('sudo su ol09')
#   videohost.sendcmd('cd ~')
   print videohost.sendcmd('whoami; pwd')

   Handler = MyRequestHandler
   server = SocketServer.TCPServer(('0.0.0.0', 8070), Handler)
   server.serve_forever()

