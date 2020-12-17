import time
import serial
import re
import sys
import os

from ona.netfpga import *
from ona.itugrid import *

def reset_pon():
    onu.reset(1)
    #time.sleep(2)
    olt_primary.reset(1)
    #olt_secondary.reset(1)
    #onu.reset(1)
    

itu=itugrid()
itu_down_red = 21
itu_up_red = 32.5
wss_red = itu.wss(itu_up_red)
wss_green = itu.wss(itu_up_green)
fpga_down_red = itu.fpga(itu_down_red)
fpga_up_red = itu.fpga(itu_up_red)


debuglevel=1

#Connect to FPGA objects
onu=Netfpga('/dev/USBonu',debuglevel=debuglevel)
olt_primary=Netfpga('/dev/USBp_olt',debuglevel=debuglevel)

print "Setting up FPGAs ..."
state=True
for f in ['/dev/USBonu', '/dev/USBp_olt']:#'/dev/USBs_olt'
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


#Disable protection - it causes problems here
olt_primary.writereg(80,1)
olt_secondary.writereg(80,1)
#set laser colours
olt_primary.set_ds_laser(fpga_down_red)
onu.writereg(6,int(fpga_up_red))


# Need to make sure ONU is registered
onu_status=onu.getstatus()
count =0
while onu_status != '10105':
   print "%d setting primary path at ONU" % count
   count=count+1
   if onu_status == '10005':
     onu.reset(1)
   else:
     reset_pon()
   onu_status = onu.getstatus
print "Connected ONU to Primary OLT"

#Add new Alloc Ids
#Alloc ID 1 is default and enabled at registration
#Going to add 2, 3 and 4 to handle traffic with 
olt_primary.writereg('e','12002')#ONU 1, Cam position 1, New Alloc ID 2
alloc_id_status = onu.readreg(20)
if alloc_id_status == '10002'
   print 'Alloc ID 2 added sucessfully'
olt_primary.writereg('e','14003')#ONU 1, Cam position 2, New Alloc ID 3
alloc_id_status = onu.readreg(21)
if alloc_id_status == '10003'
   print 'Alloc ID 3 added sucessfully'

olt_primary.writereg('e','16004')#ONU 1, Cam position 3, New Alloc ID 4
alloc_id_status = onu.readreg(21)
if alloc_id_status == '10004'
   print 'Alloc ID 4 added sucessfully'


 
True:
    print "Setting Primary Path"
    #onu.writereg(6,int(fpga_up_red))
    onu.set_filter_secondary_path()
    onu.writereg(6,int(fpga_up_red))
    time.sleep(1)
    onu_status=onu.getstatus()
    count = 1
    while onu_status != '10105':
        print "%d setting primary path at ONU" % count
        count=count+1
        if onu_status == '10005':
	   onu.reset(1)
        else:
        #sometimes the laser doesn't tune
        #I am building a fix for this
          onu.writereg(6,21)
          onu.writereg(6,int(fpga_up_red))
          reset_pon()
        onu_status = onu.getstatus()
    print "Connected ONU to Primary OLT"
    time.sleep(5)
    print "Setting Secondary Path"
    # Changing the path from primary (red) to secondary (green)
    #onu.writereg(6,int(fpga_up_green))
    onu.set_filter_primary_path() 
    onu.writereg(6,int(fpga_up_green))
    time.sleep(1)
    onu_status=onu.getstatus()
    count = 1
    while onu_status != '20105':
        print "%d setting secondary path at ONU" % count
        print onu_status
        count=count+1
        if onu_status == '20005':
          onu.reset(1)
        else:
          onu.writereg(6,21)
          onu.writereg(6,int(fpga_up_green))
          reset_pon()
        onu_status = onu.getstatus()
    print "Connected ONU to Secondary OLT"
    time.sleep(5)
    

