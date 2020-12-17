from ona.netfpga import *
from ona.pronto import *
from ona.polatis import *
from services import *
from tcdtestbed.server import *
from ona.zmqbroker import *
import time
import subprocess
import sys
import re
import threading
import os.path
from helper import *

cmd="sudo stdbuf -i0 -o0 -e0 ngrep -l -qt -d wan -xX 040033445506 dst port 6633"

# cmd="sudo ngrep -d wan -q '.' -l  icmp"

Lock=True

# Broker Stuff
class zmqsub(zmqSubscriber):
  def process(self,mst,msg):
    print "timestamp=%s, msg=%s" %(mst,msg)

class zmqLogger(zmqSubscriber):
  def __init__(self,category="Category",logfile='/tmp/zmqlogfile.txt'):
    self.logfile=logfile
    self.category=category
    self.logfilehandle=open(logfile,'a')
    super(zmqLogger,self).__init__(self.category)

  def __del__(self):
    self.logfilehandle.close()

  def process(self,mst,msg):
    self.logfilehandle.write("%s %s" %(mst,msg))

class LoggerThread(threading.Thread):
  def run(self):
    l=zmqLogger('NetEvent')

class BrokerThread(threading.Thread):
  def run(self):
    a=zmqBroker()

# BrokerThread().start()
# LoggerThread().start()
# logger=zmqSender('NetEvent')

class monio(object):
  def __init__(self,command,pattern):
    self.command=command
    self.pattern=pattern
    popen = subprocess.Popen(self.command, stdout=subprocess.PIPE, shell=True)
    while True:
        line = popen.stdout.readline()
#    lines_iterator = iter(popen.stdout.readline, b"")
#    for line in lines_iterator:
        match=re.search(r'%s'%self.pattern,line)
        if match:
          self.process(line)
#          sys.stdout.flush()
#          sys.stdin.flush()

  def process(self,line):
    sys.stdout.write(">>>>"+line)

class monIO(monio):
  def process(self,line):
    print mstime(),"point 0"
    if not Lock:
      print mstime(),"point 1"
      plts.fulldisconn(5,25)
      plts.fullconn(7,27)
#      plts.fullconn("7&5","27&20")
#      pronto.sendcmd("/ovs/bin/ovs-ofctl del-flows br0 --strict 'priority=90,in_port=20,actions=output:2'")
#      pica8.sendcmd("/ovs/bin/ovs-ofctl del-flows br0 --strict 'priority=90,in_port=20'")
#      pica8.addFlow(0,"priority=90,in_port=20,actions=output:8")
      pica8.sendcmd("/ovs/bin/ovs-ofctl del-flows br0 --strict 'priority=90,in_port=20'; /ovs/bin/ovs-ofctl add-flow br0 priority=90,in_port=20,actions=output:8")
      print mstime(),"point 2"
#     logger.tx('Alien Packet arrives')
      sys.stdout.write("Alien Packet: "+line)
    else:
      print "missed Alien packet"

class alienpktHandler(threading.Thread):
  def run(self):
     aph=monIO(cmd,'6633')

def reset_pon():
    onu.reset(1)
    olt_primary.reset(1)
#    olt_primary.reset(1)
#    olt_primary.reset(1)
    olt_secondary.reset(1)
#    time.sleep(0.5)
#    onu.reset(1)

# Set up POX Controller
pox('ol08').restart()

# Set up Pronto
print "Setting up the Pronto ..."
pronto=Pronto('10.10.10.11')
pica8=remote('10.10.10.11')
hard_bounce=False
hard_bounce=True
OVS_PORT=6633; SFLOW_PORT=6343;
CONTROLLER="10.10.10.50"; CONTROL_PORT=6633;

if hard_bounce:
        print "Hard bouncing pronto"
        # First of all, Configure the bridges and the Controller
        pronto.resetOVS(OVS_PORT,SFLOW_PORT,1)
        pronto.addBridge(0)
        pronto.addPortBridge(0,2)
        pronto.addPortBridge(0,8)
        pronto.addPortBridge(0,14)
        pronto.addPortBridge(0,20)
        pronto.delDefFlows(0)
        pronto.addBridge(1)
        pronto.addPortBridge(1,26)
        pronto.addPortBridge(1,28)
        pronto.delDefFlows(1)
        pronto.addBridge(2)
        pronto.addPortBridge(2,36)
        pronto.addPortBridge(2,38)
        pronto.delDefFlows(2)
        pronto.connectBridgeController(0,CONTROLLER,CONTROL_PORT)
pronto.addFlow(0,"priority=100,dl_src=04:00:33:44:55:06,actions=CONTROLLER:65535")
pronto.addFlow(0,"priority=90,in_port=2,actions=output:20")
pronto.addFlow(0,"priority=90,in_port=8,actions=output:20")

# upstream and downstream Bridge 1
pronto.addFlow(1,"in_port=26,actions=output:28")
pronto.addFlow(1,"in_port=28,actions=output:26")

# upstream and downstream Bridge 2
pronto.addFlow(2,"in_port=36,actions=output:38")
pronto.addFlow(2,"in_port=38,actions=output:36")


print "Setting up FPGAs ..."
state=True
for f in ['/dev/USBonu', '/dev/USBp_olt', '/dev/USBs_olt']:
  if not os.path.lexists(f):
     print "FGPA interface %s not found" % f
     state=False
if not state:
  print "All FGPA Interfaces are not operational. Please correct and rerun"
  exit()
else:
  print "FPGA interfaces look fine. Proceeding"

debuglevel=0
onu=Netfpga('/dev/USBonu',debuglevel)
olt_primary=Netfpga('/dev/USBp_olt',debuglevel)
olt_secondary=Netfpga('/dev/USBs_olt',debuglevel)

# Set up Polatis Switch
print "Seting up Polatis Switch ..."
plts = Polatis('10.10.10.24','3082')
plts.login()
plts.settimeout(60)
plts.clearallconn()
plts.fullconn('1&3','29&31')

# Alien Packet Handler
alienpktHandler().start()

# logger.tx('System Start')
while True:
#  logger.tx('Resetting to Primary Path')
  # Reset
  Lock=True
  plts.fullconn(5,25)
  plts.fulldisconn(7,27)
  reset_pon()
  while not onu.getstatus() in ['10105']:
     reset_pon()
     time.sleep(1)
     print "ONU was failed status of %s" % onu.getstatus()
  print "PON reset with ONU status: %s" % onu.getstatus()
  pica8.sendcmd("/ovs/bin/ovs-ofctl del-flows br0 --strict 'priority=90,in_port=20'")
  pica8.addFlow(0,"priority=90,in_port=20,actions=output:2")
#  pronto.sendcmd("/ovs/bin/ovs-ofctl del-flows br0 --strict 'priority=90,in_port=20,actions=output:8'")
#  pronto.addFlow(0,"priority=90,in_port=20,actions=output:2")
  Lock=False
  print "\007",
  time.sleep(1)
  print "\007",
  print
  print mstime(),"Breaking Fibre now  .."
#  x=raw_input()
  # Failover
#  logger.tx('Breaking Primary Path')
#   plts.fulldisconn(5,25) # Break Path .. and then wait
  olt_primary.sendcmd('t')
  time.sleep(1.5)
  print "PON failover with ONU status: %s" %onu.getstatus()
  print "\007",
  print "Press to Reset .."
  time.sleep(1.5)
#  x=raw_input()
#logger.tx('System Stop')

plts.logout()
pronto.logout()
