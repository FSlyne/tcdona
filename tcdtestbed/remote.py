import datetime
import socket
import sys

def mstime():
  t=datetime.datetime.now()
  return t.strftime('%s.%%06d') % t.microsecond

class remote(object):
   def __init__(self, server, port=10000):
      self.server = server
      self.port = port

   def sendcmd(self,cmd):
      data = ''
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.server_address = (self.server, self.port)
      try:
         sent = self.sock.sendto(cmd, self.server_address)
         data, server = self.sock.recvfrom(4096)
      finally:
         self.sock.close()
      return data

   def addFlow(self,bridge,flow):
      self.sendcmd('ovs-ofctl add-flow br'+str(bridge)+' '+flow)

   def xFlow(self,bridge,flow):
      self.sendcmd('ovs-ofctl del-flow br'+str(bridge)+' '+flow);

