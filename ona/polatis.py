import sys
import telnetlib
import re

class Polatis():

    def __init__(self,host,port):
        self.telnet = telnetlib.Telnet(host,port)
        self.eol = ";"

    def __del__(self):
        pass

    def sendcmd(self,line):
#        print "sending " + line
        self.telnet.write(line + "\n")
        return  self.telnet.read_until(self.eol)

    def login(self):
        return self.sendcmd('ACT-USER::root:123::root;')

    def logout(self):
#        print self.telnet.read_all()
        self.sendcmd('CANC-USER::root:123:;')
        self.telnet.close()

    def settimeout(self,timeout=60):
        return self.sendcmd('ED-EQPT::TIMEOUT:123:::ADMIN='+str(timeout)+';')
      
    def clearallconn(self):
        self.sendcmd('DLT-PATCH::ALL:123:;')
    
    def inpconv(self, inport):
        return inport 
    
    def outpconv(self, outport):
        return outport
    
    def conn(self, inport,outport):
        inport = self.inpconv(inport)
        outport = self.outpconv(outport)
        line = 'ENT-PATCH::'+ str(inport) +','+ str(outport)+':123:;'
        return self.sendcmd(line)
                            
    def disconn(self, inport,outport):
        inport = self.inpconv(inport)
        outport = self.outpconv(outport)
        line = 'DLT-PATCH::'+str(inport)+':123:;'
        return self.sendcmd(line)
    
    def fullconn(self,inport,outport):
        self.conn(inport,outport)
        
    def fulldisconn(self,inport,outport):
        self.disconn(inport,outport)

    def getpatch(self):
        line ='RTRV-PATCH:::123:;'
        lines = self.sendcmd(line)
        ret=''
        for line in lines.split("\n"):
           m=re.match("\W*\"(\d+),(\d+)\"",line)
           if m:
              ret=ret+"%s<->%s; " %(m.group(1), m.group(2))
        return ret 

    def getstatus(self, port,dr):
        sigtype = self.getwaveband(port,dr)
        if (dr > 0):
            port = self.outpconv(port)
        else:
            port = self.inpconv(port)

        cmd = 'rtrv-crs-fiber::'+str(port)+':1;'
        line =  self.sendcmd(cmd)
        lines = line.split('\n')
        
        iportid =  ''
        iportname =  ''
        oportid =  ''
        oportname =  ''
        connid =  ''
        connstate =  ''
        conncause =  ''
        inpwr =  ''
        outpwr =  ''
        pwrloss =  ''

        for line in lines:
            matchObj = re.match( r'IPORTID=(.*),IPORTNAME=(.*),OPORTID=(.*),OPORTNAME=(.*),CONNID=(.*),CONNSTATE=(.*),CONNCAUSE=(.*),INPWR=(.*),OUTPWR=(.*),PWRLOSS=(.*)', line, re.M|re.I)
            if matchObj:
                iportid = matchObj.group(1)
                iportname = matchObj.group(2)
                oportid = matchObj.group(3)
                oportname = matchObj.group(4)
                connid = matchObj.group(5)
                connstate = matchObj.group(6)
                conncause = matchObj.group(7)
                inpwr = matchObj.group(8)
                outpwr = matchObj.group(9)
                pwrloss = matchObj.group(10)
        return port, connstate, conncause, inpwr, outpwr, pwrloss, sigtype
           
    def getwaveband(self, port,dr):
        if (dr > 0):
            port = self.outpconv(port)
        else:
            port = self.inpconv(port)
        cmd = 'rtrv-sigtype-fiber::'+str(port)+':2;'
        line =  self.sendcmd(cmd)
        lines = line.split('\n')
        print "gwb: ", line
        for line in lines:
            matchObj = re.match( r'.*PORTID=(.*),PORTNAME=(.*),SIGTYPE=(\d+).*', line, re.M|re.I)
            if matchObj:
                return matchObj.group(3)
            
    def setPrimaryPath(self, PortA, PortB):
        self.PA = PortA
        self.PB = PortB
        
    def setSecondaryPath(self, PortA, PortB):
        self.SA = PortA
        self.SB = PortB
        
    def conPrimary():
        self.fullconn(self.PA, self.PB)
        
    def conSecondary():
        self.fullconn(self.SA, self.SB)
        
    def disPrimary():
        self.fulldisconn(self.PA, self.PB)
        
    def disSecondary():
        self.fulldisconn(self.SA, self.SB)
        
    def upPdownS(self):
        self.conPrimary()
        self.disSecondary()
        
    def upSdownP(self):
        self.conSecondary()
        self.disPrimary()

