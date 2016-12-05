import time
import serial
import re
import sys
import os

from ona.netfpga import *
from ona.tunablefilters import *
from ona.netfpga import *
from ona.itugrid import *

def reset_pon():
    onu.reset(1)
    #time.sleep(2)
    olt_primary.reset(1)
    olt_secondary.reset(1)
    #onu.reset(1)
    

itu=itugrid()
itu_down_red = 21
itu_down_green = 23
itu_up_red = 32.5
itu_up_green = 31
wss_red = itu.wss(itu_up_red)
wss_green = itu.wss(itu_up_green)
fpga_down_red = 21#itu.fpga(itu_down_red)
fpga_down_green = 26 #itu.fpga(itu_down_green)
fpga_up_red = itu.fpga(itu_up_red)
fpga_up_green = itu.fpga(itu_up_green)

debuglevel=0

#wss=wss('/dev/USBwss',debuglevel)
onu=Netfpga('/dev/USBonu',debuglevel)
olt_primary=Netfpga('/dev/USBp_olt',debuglevel)
olt_secondary=Netfpga('/dev/USBs_olt',debuglevel)
print "Setting up FPGAs ..."
state=True
for f in ['/dev/USBonu', '/dev/USBp_olt','/dev/USBs_olt','/dev/USBwss']:#'/dev/USBs_olt'
  if not os.path.lexists(f):
     print "FGPA interface %s not found" % f
     state=False
if not state:
  print "All FGPA Interfaces are not operational. Please correct and rerun"
  exit()
else:
  print "FPGA interfaces look fine. Proceeding"

if onu.tunable_laser():
   print "ONU Laser is Tunable"
if olt_primary.tunable_laser():
   print "OLT1 Laser is Tunable"
if olt_secondary.tunable_laser():
   print "OLT2 Laser is Tunable"

#Disable protection - it causes problems here
olt_primary.writereg(80,1)
olt_secondary.writereg(80,1)
#set laser colours
olt_primary.set_ds_laser(fpga_down_red)
olt_secondary.set_ds_laser(fpga_down_green)
#onu.writereg(6,int(fpga_up_red))
onu.set_filter_secondary_path()
onu.writereg(6,int(fpga_up_red))

#print wss.sab()
#print wss.ura(wss_red,4,0)
#print wss.ura(wss_green,5,0)
#print wss.rsw()
#print wss.rra()
#Ready to start testing
reset_pon();
while True:
    print "Setting Primary Path"
    #onu.writereg(6,int(fpga_up_red))
    #onu.set_filter_secondary_path()
    #onu.writereg(6,int(fpga_up_red))
    #time.sleep(1)
    onu_status=onu.getstatus()
    count = 1
    while  onu_status != '10105':
        print "%d Failed to find Primary path resetting experiment"
        print onu_status
        if onu_status == '10005':
	   onu.reset(1)
        #else:
        #sometimes the laser doesn't tune
        #I am building a fix for this
        onu.writereg(6,21)
        onu.writereg(6,int(fpga_up_red))
        onu.set_filter_primary_path()
        onu.set_filter_secondary_path()
        reset_pon()
        onu_status = onu.getstatus()
    print "Connected ONU to Primary OLT"
    #attempt to move ONU to Secondary Path
    #due to bug in OLT need to flush register 8
    olt_primary.sendcmd('w8:120033')
    olt_primary.sendcmd('w8:1012a')
    time.sleep(1)
    if onu.getstatus() != '20105':
       print 'Failed to migrate, Terminating'
       break
    else:
      #It worked
      print "Connected ONU to Secondary OLT"
      time.sleep(5)
      #Try to move back
      olt_secondary.sendcmd('w8:120033')
      olt_secondary.sendcmd('w8:1022d')
    
     

