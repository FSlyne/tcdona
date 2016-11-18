import time
import serial
import re


class edfa():
    def __init__(self, COM_PORT,debuglevel=0):
        self.ser = serial.Serial(COM_PORT,
                            baudrate = 57600,
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
        count = 1
        while True:
           if self.ser.inWaiting():
              resp = self.ser.read(self.ser.inWaiting())
              break
           else:
              count = count+1
              time.sleep(0.1)
              if count > 10:
                 break
        return resp

    def sendcmd(self,line):
        if self.debuglevel > 0:
           print self.device,"\t",line
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

    def set_smode(self,stage,db):
        return self.sendcmd("smode %s g %s" % (str(stage), str(db)))

    def get_smode(self):
        list = []
        l = self.sendcmd('smode')
        for line in l.split('\n'):
           matchObj = re.match( r'SMODE (.*): G (.*) dB.*', line, re.M|re.I)
           if matchObj:
              list.append(matchObj.group(2))
        return list

    def get_pd(self):
        list = []
        l = self.sendcmd('pd')
        for line in l.split('\n'):
           matchObj = re.match( r'PD (.*): (.*) dBm.*', line, re.M|re.I)
           if matchObj:
              list.append(matchObj.group(2))
        return list


