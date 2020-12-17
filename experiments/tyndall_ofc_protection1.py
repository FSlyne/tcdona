from ona.netfpga import *
from ona.pronto import *
from ona.polatis import *
from tcdtestbed.server import *
import time
import subprocess
import sys
import re
from helper import *

swtime=10

cmd="sudo ngrep -l -qt -d wan -xX 040033445506 port 6633"
cmd="sudo ngrep -d wan -q '.' -l  icmp"

class monio(object):
  def __init__(self,command,pattern):
    self.command=command
    self.pattern=pattern
    popen = subprocess.Popen(self.command, stdout=subprocess.PIPE, shell=True)
    lines_iterator = iter(popen.stdout.readline, b"")
    for line in lines_iterator:
        match=re.search(r'%s'%self.pattern,line)
        if match:
           self.process(line)
           sys.stdout.flush()

  def process(self,line):
    sys.stdout.write(">>>>"+line)

class monIO(monio):
  def process(self,line):
    sys.stdout.write("++++"+line)

def reset_pon():
    onu.reset(1)
    olt_primary.reset(1)
    olt_secondary.reset(1)

# Setting up Pronto
print "Setting up the Pronto ..."
pronto=Pronto('10.10.10.11')
# Set up Pront
hard_bounce=False
OVS_PORT=6633; SFLOW_PORT=6343;
CONTROLLER="10.10.10.5"; CONTROL_PORT=6633;

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

# pronto.connectBridgeController(0,CONTROLLER,CONTROL_PORT)
# downstream Bridge 0
pronto.addFlow(0,"in_port=2,actions=output:20")
pronto.addFlow(0,"in_port=8,actions=output:20")

# upstream and downstream Bridge 1
pronto.addFlow(1,"in_port=26,actions=output:28")
pronto.addFlow(1,"in_port=28,actions=output:26")

# upstream and downstream Bridge 2
pronto.addFlow(2,"in_port=36,actions=output:38")
pronto.addFlow(2,"in_port=38,actions=output:36")

# Setting up FPGA's
print "Setting up FPGA's ..."
debuglevel=0
onu=Netfpga('/dev/USBonu',debuglevel)
olt_primary=Netfpga('/dev/USBp_olt',debuglevel)
olt_secondary=Netfpga('/dev/USBs_olt',debuglevel)

# Setting up Polatis
print "Setting up the Polatis ..."
plts = Polatis('10.10.10.24','3082')
plts.login()
plts.settimeout(60)
plts.clearallconn()
plts.fullconn('1&3','29&31')

pica8 = remote('10.10.10.11')

print "Entering the Routiner ..."
while True:
  # Reset
  plts.fulldisconn('3&7','31&27')
  plts.fullconn('1&5','29&25')
  #plts.fulldisconn('3&7','31&27')
  pica8.xFlow(0,"in_port=20")
  pica8.addFlow(0,"in_port=20,actions=output:2")
  reset_pon()
  print "PON reset with ONU status: %s" % onu.getstatus()
  print "Polatis patch: %s" % plts.getpatch()
  print "\007",
  time.sleep(0.5)
  print "\007",
  time.sleep(swtime)
#  print "Press to Failover .."
#  x=raw_input()
  # Failover
  plts.fulldisconn('1&5','29&25')
  plts.fullconn('3&7','31&27')
  #plts.fulldisconn('1&5','29&25')
  pica8.xFlow(0,"in_port=20")
  pica8.addFlow(0,"in_port=20,actions=output:8")
  print "PON failover with ONU status: %s" %onu.getstatus()
  print "Polatis patch: %s" % plts.getpatch()
  print "\007","\007",
  time.sleep(swtime)
#  print "Press to Reset .."
#  x=raw_input()

plts.logout()
pronto.logout()
