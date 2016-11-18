import time
import serial
import re


class Netfpga():
    def __init__(self, COM_PORT,debuglevel=0):
        self.ser = serial.Serial(COM_PORT,
                            baudrate = 460800,
                            bytesize = 8,
                            parity = 'N',
                            stopbits = 1,
                            timeout=0,
                            xonxoff=0,
                            rtscts=0
			)
        self.device=COM_PORT
        self.debuglevel=debuglevel

    def __del__(self):
        self.ser.close
        
    def sendcmd2(self,line):
        resp=''
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(line)
        time.sleep(0.1)
        while True:
           if self.ser.inWaiting():
              resp = self.ser.read(self.ser.inWaiting())
              break
           else:
              time.sleep(0.1)
        return resp
 
    def sendcmd(self,line):
        if self.debuglevel > 0:
           print self.device,"\t",line
        if self.debuglevel < 2:
           return self.sendcmd2(line+"\r\n")
        else:
           return

    def read(self):
        return self.ser.read(size=100)

    def readline(self):
        return self.ser.readline()
        
    def trigger(self):
        self.sendcmd('t')
        
    def reset(self,t=0):
        self.sendcmd('r')
        if t>0:
           time.sleep(t)

    def enable_mpls(self):
        print "Setting MPLS"
        return self.sendcmd('wc014:1')

    def disable_mpls(self):
        print "Unsetting MPLS"
        return self.sendcmd('wc014:0')

    def set_ds_laser(self,fpga_channel):
        fpga_channel = int(fpga_channel)
        print ">>>>",fpga_channel
        fpga_hex=str("%02x" % fpga_channel)
        cmd = 'w7:'+fpga_hex
        return self.sendcmd(cmd) 

    def set_us_laser(self,onu_id,dd,fpga_channel):
        onu_hex= str("%04x" % onu_id)
        dd_hex= str("%02x" % dd)
        fpga_hex = str("%02x" % fpga_channel)
        cmd = 'w8:'+ onu_hex + dd_hex + fpga_hex
        return self.sendcmd(cmd)

    def tunable_laser(self):
        if self.readreg('c') == '1':
           return True
        else:
           return False

    def laser_wavelength(self):
        return self.readreg('d')

    def set_alloc_id(self, onu_id, alloc_id):
        onu_hex = str("%03x"%onu_id)
        alloc_hex = str("%04x"%alloc_id)
        cmd = 'we:0'+onu_hex+alloc_hex
        return self.sendcmd(cmd)

    def create_flow(self,mac,xgem,mpls_tag,match,cam):
        xgem_hex= str("%04x" % xgem)
        mpls_hex = str("%05x" % mpls_tag)
        cam_hex = str("%02x" % cam)
        mac_clean=str(mac).replace(':','').ljust(12,'0')
        cmd1 = mac_clean[-8:]; self.sendcmd('wc010:'+cmd1);
        cmd2 = xgem_hex+mac_clean[:4]; self.sendcmd('wc011:'+cmd2);
        cmd3 = cam_hex+str(match)+mpls_hex; self.sendcmd('wc012:'+cmd3);                

    def delete_flow(self,cam):
        self.create_flow(0,0,0,0,cam) 

    def dwa_set(self):
        return self.sendcmd('w8:1001a')

    def dwa_reset(self):
        return self.sendcmd('w8:10015')

    def getstatus(self):
        resp = self.sendcmd2('s')
        try:
           searchObj = re.match( r'Status: (.*)', resp, re.M|re.I)
  #         print "getstatus debug: ",searchObj.group(1)
           return searchObj.group(1)
        except:
           print "getstatus error: ",resp
           return "00000"

    def readreg(self,reg):
        resp = self.sendcmd('x'+str(reg))
        searchObj = re.match( r'Read (.*) : (.*)', resp, re.M|re.I)
        return searchObj.group(2)

    def writereg(self,reg,val):
        self.sendcmd('w'+str(reg)+':'+str("%02x" % val))

    def set_wss_primary_path(self):
        self.writereg('f',1)
        time.sleep(1)
        self.writereg('f',0)

    def set_wss_secondary_path(self):
        self.writereg('f',2)
        time.sleep(1)
        self.writereg('f',0)

    def set_filter_primary_path(self):
        self.writereg('f',1)
        #time.sleep(1)
        #self.writereg('f',0)

    def set_filter_secondary_path(self):
        self.writereg('f',2)
       # time.sleep(1)
       # self.writereg('f',0)


def reset_pon2():
    olt_primary.reset(1)
    olt_secondary.reset(1)
    onu.reset(1)
    # Enable MPLS lookup
    olt_primary.enable_mpls()
    olt_secondary.enable_mpls()
    # Set ONU to listen for XGEM on red path
    olt_primary.set_alloc_id(1,red_alloc_id)
    # Backward Compatibility
    olt_primary.sendcmd('wc013:00001234')
    olt_secondary.sendcmd('wc013:00001234')
    # Set up Flow
    olt_primary.create_flow(0,red_alloc_id,red_pw_tag,2,0)
    olt_secondary.delete_flow(0)
    olt_secondary.delete_flow(1)

def set_pon2():
    # Run Test
    # Set up red flow on secondary OLT
    olt_secondary.create_flow(0,red_alloc_id,red_pw_tag,2,0);
    # set up green flow on secondary OLT
    olt_secondary.create_flow(0,green_alloc_id,green_pw_tag,2,1);
    # Add new Alloc id to ONU to minimise downtime
    olt_primary.set_alloc_id(1,green_alloc_id);
    # DWA switchover to channel 15 and secondary DS link
    olt_primary.set_us_laser(1,1,green_laser_no);
    olt_primary.sendcmd('w8:10011');
    # Delete flow from Old OLT stored at position 0
    olt_primary.delete_flow(0);


if __name__ == "__main__":
  red_pw_tag=2001; red_alloc_id = 40;
  green_pw_tag=2003; green_alloc_id = 50;
  red_laser_no=21;
  green_laser_no=26;

  debuglevel=1

  onu=Netfpga('/dev/USBonu',debuglevel)
  olt_primary=Netfpga('/dev/USBp_olt',debuglevel)
  olt_secondary=Netfpga('/dev/USBs_olt',debuglevel)

  onu.writereg('f',1);

  if onu.tunable_laser():
    print "ONU Laser is Tunable"
  if olt_primary.tunable_laser():
    print "OLT1 Laser is Tunable"
  if olt_secondary.tunable_laser():
    print "OLT2 Laser is Tunable"

  olt_primary.set_ds_laser(red_laser_no)
  olt_secondary.set_ds_laser(green_laser_no)

  print "OLT1 Laser is set to %s" % olt_primary.laser_wavelength()
  print "OLT2 Laser is set to %s" % olt_secondary.laser_wavelength()

  while True:
    onu_status=onu.getstatus()
    count = 1
    while onu_status != '10105':
       print "got back %s from ONU so attempt to reset (attempt %s)" % (onu_status, count)
       count=count+1
       reset_pon()
       onu_status = onu.getstatus()
    print "pon reset with ONU status", onu.getstatus()
    time.sleep(10)
    print "Now setting pon ..."
    set_pon()
    print "... within ONU status", onu.getstatus()
    time.sleep(10)

    print onu.readreg(5)
    print olt_primary.readreg(5)
    print olt_secondary.readreg(5)
