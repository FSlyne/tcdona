
from ona.tunablefilters import *
from ona.netfpga import *
from ona.itugrid import *

import time


ituno="20"

def reset_pon():
    olt_primary.reset(1)
    onu.reset(1)

if __name__ == "__main__":
#   dicon=dicon_tunablefilter('/dev/USBopticalfilter')
   olt_primary=Netfpga('/dev/USBp_olt')
   onu=Netfpga('/dev/USBonu')
   itu=itugrid()
#   print dicon.setWA(itu.nm(ituno))
#   print dicon.getWA() # check that it is set to the desired Wavelength
   if olt_primary.tunable_laser():
      print "OLT1 Laser is Tunable"
   else:
      print "OLT1 Laser does not appear to be Tunable"

   olt_primary.set_ds_laser(itu.fpga(ituno))
   print "OLT1 Laser is set to %s" % olt_primary.laser_wavelength()

   onu_status = onu.getstatus()
   count = 1
   while onu_status != '10105':
      print "got back %s from ONU so attempt to reset (attempt %s)" % (onu_status, count)
      reset_pon()
      onu_status = onu.getstatus()
      count=count+1
      time.sleep(2)

   print "ONU status is ",onu_status
