from tcdtestbed.server import *
import time

class eventlog(tbserver):

   def __init__(self,server):
      super(eventlog,self).__init__()

   def __del__(self):
      super(eventlog,self).__del__()

   def stop(self):
      self.killProcess('eventlog.pl')
      return self.killProcess('socat')

   def start(self):
      self.cd('/home/fslyne/netfpga')
      return self.nohup('perl eventlog.pl')

   def restart(self):
      self.stop()
      time.sleep(1)
      return self.start()

class pox(tbserver):

#   def __init__(self,server):
#      super(pox,self).__init__()

#   def __del__(self):
#      super(pox,self).__del__()

   def stop(self):
      return self.killProcess('pox')

   def start(self):
      self.cd('/home/ol08/pox')
      return self.nohup('./pox.py misc.protection_controller')

   def restart(self):
      self.stop()
      time.sleep(1)
      return self.start()

