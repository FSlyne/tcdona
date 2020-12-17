import time
import serial
import re
import sys
import os

from ona.netfpga import *
from ona.tunablefilters import *
from ona.netfpga import *
from ona.itugrid import *
from ona.pronto import *
from ona.polatis import *
from tcdtestbed.server import *
from helper import *

itu=itugrid()
itu_down_red = 55.5
itu_down_green = 54.5
itu_up_red = 31.5
itu_up_green = 32.5 
fpga_down_red = itu.fpga(itu_down_red)
#Filter and Laser are off by one in ITU table
#However laser and Wss look to be aligned so technically both Laser adn WSS values are wrong compared to filter values
fpga_down_green = itu.fpga(itu_down_green)
fpga_up_red = itu.fpga(itu_up_red) 
fpga_up_green = itu.fpga(itu_up_green)

nm_down_green=itu.nm(itu_down_green)
nm_down_red=itu.nm(itu_down_red)
nm_up_green=itu.nm(itu_up_green)
nm_up_red=itu.nm(itu_up_red)

class dwa_pon(object):
    
    def __init__(self):
        self.debug = 1
        self.onu=Netfpga('/dev/USBonu',debuglevel=self.debug)
        self.olt_primary=Netfpga('/dev/USBp_olt',debuglevel=self.debug)
        self.olt_secondary=Netfpga('/dev/USBs_olt',debuglevel=self.debug)
        #Seamas' contribution to this script completely out of place but it works     
        while '5' in self.onu.getstatus():
          self.onu.reset(1)
          time.sleep(1)
        self.delay=20
        
    def check_interfaces(self):
        print "Setting up FPGAs ..."
        state=True
        for f in ['/dev/USBonu', '/dev/USBp_olt', '/dev/USBs_olt','/dev/USBwss']:
          if not os.path.lexists(f):
             print "FGPA interface %s not found" % f
             state=False
        if not state:
          print "All FGPA Interfaces are not operational. Please correct and rerun"
          exit()
        else:
          print "FPGA interfaces look fine. Proceeding"


    def baseline(self):
        #Disable protection - it causes problems here
        self.olt_primary.writereg(80,1)
        self.olt_secondary.writereg(80,1)
        #set laser colours
        self.olt_primary.set_ds_laser(fpga_down_red)
        self.olt_secondary.set_ds_laser(fpga_down_green)
        #onu.writereg(6,int(fpga_up_red))
        self.onu.set_filter_secondary_path()
        self.onu.writereg(6,int(45))#fpga_up_red))
        self.reset()
          
    def check_tunability(self):
        if self.onu.tunable_laser():
           print "ONU Laser is Tunable"
        if self.olt_primary.tunable_laser():
           print "OLT1 Laser is Tunable"
        if self.olt_secondary.tunable_laser():
           print "OLT2 Laser is Tunable"

    def set_primary_path(self):
        print "Setting Primary Path"
        time.sleep(2)
        onu_status=self.onu.getstatus()
        print "1. ONU status %s " % onu_status
        count = 1
        while not onu_status in ['10105']:
          print "%d setting primary path at ONU status = %s" % (count, onu_status)
          count=count+1
          if onu_status == '10005':
            self.onu.reset(1)
          else:
            self.reset()
          onu_status = self.onu.getstatus()
        self.post_primary()
        print "Connected ONU to Primary OLT"
        time.sleep(self.delay)
    
    def set_secondary_path(self):
        print "Setting Secondary Path"
        #to get around a bug
        self.olt_primary.sendcmd('w8:222222')
        self.olt_primary.sendcmd('w8:1012b') 
        time.sleep(2)
        onu_status=self.onu.getstatus()
        count = 1
        print "2. ONU status %s " % onu_status
        if onu_status in ['20105']:
          print "Connected ONU to Secondary OLT"
          #commeded out because pronto died
          self.post_secondary()
          time.sleep(self.delay)
          self.olt_secondary.sendcmd('w8:222222')
          self.olt_secondary.sendcmd('w8:1022d')
        else:
          #switch over failed reset pon and start againi
          print "Failed to get OLT 2 so resetting hardware"
          self.reset()

    def set_optical_path(self):
        # Setting up Polatis
        print "Setting up the Polatis ..."
        self.plts = Polatis('10.10.10.24','3082')
        self.plts.login()
        self.plts.settimeout(60)
        self.plts.clearallconn()
        self.plts.fullconn('1','29')
        self.plts.fullconn('2','31')
        self.plts.fullconn('5','25')
        self.plts.fullconn('7','26')
          
    def pre_primary():
        pass
    def post_primary():
        pass
    def pre_secondary():
        pass
    def post_secondary():
        pass
          
    def reset(self):
        self.onu.writereg(6,int(43))
        #self.onu.writereg(6,int(fpga_up_red))
        self.onu.writereg(6,int(45))#int(fpga_up_red))
        self.onu.set_filter_secondary_path()
        self.onu.reset(1)
        #time.sleep(2)
        self.olt_primary.reset(1)
        self.olt_secondary.reset(1)
        #onu.reset(1)


class dwap(dwa_pon):
    def __init__(self,ip,initialise=False):
        super(dwap,self).__init__()
        self.pronto=Pronto(ip)
        self.pica8=remote('10.10.10.11')
        OVS_PORT=6633; SFLOW_PORT=6343;
        CONTROLLER="10.10.10.5"; CONTROL_PORT=6633;
        if initialise:
             self.pronto.resetOVS(OVS_PORT,SFLOW_PORT,1)
             self.pronto.addBridge(0)
             self.pronto.addPortBridge(0,2)
             self.pronto.addPortBridge(0,8)
             self.pronto.addPortBridge(0,14)
             self.pronto.addPortBridge(0,20)
             self.pronto.delDefFlows(0)
             self.pronto.addBridge(1)
             self.pronto.addPortBridge(1,26)
             self.pronto.addPortBridge(1,28)
             self.pronto.delDefFlows(1)
             self.pronto.addBridge(2)
             self.pronto.addPortBridge(2,36)
             self.pronto.addPortBridge(2,38)
             self.pronto.delDefFlows(2)
        self.pronto.addFlow(0,"in_port=2,actions=output:20")
        self.pronto.addFlow(0,"in_port=8,actions=output:20")
        # upstream and downstream Bridge 1
        self.pronto.addFlow(1,"in_port=26,actions=output:28")
        self.pronto.addFlow(1,"in_port=28,actions=output:26")
        # upstream and downstream Bridge 2
        self.pronto.addFlow(2,"in_port=36,actions=output:38")
        self.pronto.addFlow(2,"in_port=38,actions=output:36")

        #super(dwap,self).__init__()       
    def post_primary(self):
        self.pica8.xFlow(0,"in_port=20")
        self.pica8.addFlow(0,"in_port=20,actions=output:2")
    def post_secondary(self):
        self.pica8.xFlow(0,"in_port=20")
        self.pica8.addFlow(0,"in_port=20,actions=output:8")
        
if __name__ == "__main__":
    dw=dwap(ip='10.10.10.11',initialise=False)
    dw.set_optical_path()
    dw.check_interfaces()
    dw.baseline()
    dw.check_tunability()
    while True:
        dw.set_primary_path()
        time.sleep(1)
        dw.set_secondary_path()
        time.sleep(1)
    

