import time
import serial
import re

class serialb(object):
    def __init__(self, COM_PORT,baudrate = 115200,debuglevel=0):
        self.device=COM_PORT
        self.debuglevel=debuglevel
        if self.debuglevel > 0:
           print "open serial port %s at rate %s" % ( COM_PORT,str(baudrate))
        self.ser = serial.Serial(COM_PORT,
                            baudrate= baudrate,
                            bytesize = 8,
                            parity = 'N',
                            stopbits = 1,
                            timeout=0,
                            xonxoff=0,
                            rtscts=0
                        )

    def __del__(self):
        self.ser.close

    def sendcmd(self,line):
        if self.debuglevel > 0:
           print self.device,"\t",line
        if self.debuglevel < 2:
           return self.sendcmd2(line+"\r\n")
        else:
           return

    def sendcmd2(self,line):
        resp=''
        self.ser.write(line)
        while True:
           if self.ser.inWaiting():
              resp = self.ser.read(self.ser.inWaiting())
              break
           else:
              time.sleep(1)
        return resp

    def read(self):
        return self.ser.read(size=100)

    def readline(self):
        return self.ser.readline()

