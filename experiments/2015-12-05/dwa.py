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

itu=itugrid()
itu_down_red = 21
itu_down_green = 23
itu_up_red = 32.5
itu_up_green = 31
wss_red = itu.wss(itu_up_red)
wss_green = itu.wss(itu_up_green)
fpga_down_red = 21#itu.fpga(itu_down_red)
#Filter and Laser are off by one in ITU table
#However laser and Wss look to be aligned so technically both Laser adn WSS values are wrong compared to filter values
fpga_down_green = 25 #itu.fpga(itu_down_green)
fpga_up_red = itu.fpga(itu_up_red)
fpga_up_green = itu.fpga(itu_up_green)

class dwa_pon(object):

    def __init__(self):
        self.debug = 0
        self.onu=Netfpga('/dev/USBonu',debuglevel=self.debug)
        self.olt_primary=Netfpga('/dev/USBp_olt',debuglevel=self.debug)
        self.olt_secondary=Netfpga('/dev/USBs_olt',debuglevel=self.debug)
        #Seamas' contribution to this script completely out of place but it works
        while '5' in self.onu.getstatus():
          self.onu.reset(1)
          time.sleep(1)
        self.delay=20

    def set_wss(self):
        self.wss=wss('/dev/USBwss')
        self.wss.sab()
        self.wss.ura(wss_red,4,0)
        self.wss.ura(wss_green,5,0)
        self.wss.rsw();
        self.wss.rra();

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
        self.onu.writereg(6,int(fpga_up_red))
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
        if self.onu.getstatus()=='20105' # Not strictly necessary but 
        #I have added it here to avoid a possible bug in the secondary OLT
        # that I haven't tested for. I don't know how the OLT reacts to getting
        # These commands if onu is not attached. So just being extra safe
          self.olt_secondary.sendcmd('w8:222222') 
          self.olt_secondary.sendcmd('w8:1022d')

        time.sleep(2)
        onu_status=self.onu.getstatus()
        print "1. ONU status %s " % onu_status
        count = 1
        while onu_status != '10105':
          print "%d setting primary path at ONU status = %s" % (count, onu_status)
          count=count+1
          if onu_status == '10005':
            self.onu.reset(1)
          else:
            self.reset()
          onu_status = self.onu.getstatus()
        self.post_primary()
        print "Connected ONU to Primary OLT with status %s" % onu_status
        time.sleep(self.delay)

    def set_secondary_path(self):
        print "Setting Secondary Path"
        #to get around a bug
        self.olt_primary.sendcmd('w8:222222')
        self.olt_primary.sendcmd('w8:1012a')
        time.sleep(2)
        onu_status=self.onu.getstatus()
        count = 1
        print "2. ONU status %s " % onu_status
        if onu_status == '20105':
          print "Connected ONU to Secondary OLT with status %s" % onu_status
          #commeded out because pronto died
          self.post_secondary()
          time.sleep(self.delay)
          # These are fine in a looping scenario but not in a function scenario
          #self.olt_secondary.sendcmd('w8:222222')
          #self.olt_secondary.sendcmd('w8:1022d')
        else:
          #switch over failed reset pon and start againi
          print "Failed to get OLT 2 so resetting hardware"
          self.reset()

    def pre_primary():
        pass
    def post_primary():
        pass
    def pre_secondary():
        pass
    def post_secondary():
        pass

    def reset(self):
        self.onu.writereg(6,int(fpga_up_green))
        self.onu.writereg(6,int(fpga_up_red))
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
        if initialise:
             self.pronto.sendcmd('bash /home/tcdonalab2.sh')
        #super(dwap,self).__init__()
    def post_primary(self):
        self.pronto.sendcmd('bash /home/tcdonalab2_redpath.sh')
    def post_secondary(self):
        self.pronto.sendcmd('bash /home/tcdonalab2_greenpath.sh')


