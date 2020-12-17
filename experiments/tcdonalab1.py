import time
import serial
import re
import sys

from ona.netfpga import *
from ona.tunablefilters import *
from ona.netfpga import *
from ona.itugrid import *
from ona.glim import *

def reset_pon():
    olt_primary.reset(1)
    olt_secondary.reset(1)
    onu.reset(1)

itu=itugrid()
itu_down_red = 21
itu_down_green = 23
itu_up_red = 32.5
itu_up_green = 31
wss_red = itu.wss(itu_up_red)
wss_green = itu.wss(itu_up_green)
fpga_down_red = itu.fpga(itu_down_red)
fpga_down_green = itu.fpga(itu_down_green)
fpga_up_red = itu.fpga(itu_up_red)
fpga_up_green = itu.fpga(itu_up_green)

debuglevel=0

glim = Glimmerglass('10.10.10.25','10034')
glim.login()
onu=Netfpga('/dev/USBonu',debuglevel)
olt_primary=Netfpga('/dev/USBp_olt',debuglevel)
olt_secondary=Netfpga('/dev/USBs_olt',debuglevel)
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

if onu.tunable_laser():
   print "ONU Laser is Tunable"
if olt_primary.tunable_laser():
   print "OLT1 Laser is Tunable"
if olt_secondary.tunable_laser():
   print "OLT2 Laser is Tunable"


olt_primary.set_ds_laser(fpga_down_red)
olt_secondary.set_ds_laser(fpga_down_green)
onu.set_filter_primary_path()
onu.ds_laser(fpga_up_red)

while True:
    print "Setting Primary Path"
    glim.fullconn(port1,port2)
    onu_status=onu.getstatus()
    count = 1
    while onu_status != '10105':
        print "%d setting primary path at ONU" % count
        count=count+1
        reset_pon()
        onu_status = onu.getstatus()
    print "Connected ONU to Primary OLT"
    time.sleep(5)
    print "Setting Secondary Path"
    # Changing the path from primary (red) to secondary (green)
    glim.fullconn(port1,port2)
    onu_status=onu.getstatus()
    count = 1
    while onu_status != '10105':
        print "%d setting secondary path at ONU" % count
        count=count+1
        reset_pon()
        onu_status = onu.getstatus()
    print "Connected ONU to Secondary OLT"
    time.sleep(5)
    
glim.logout()
    

