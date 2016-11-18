from ona.serialbase import *

class dicon_tunablefilter(serialb):
    def __init__(self, COM_PORT,baudrate=115200,debuglevel=0):
        super(dicon_tunablefilter,self).__init__(COM_PORT,baudrate,debuglevel)

    def diag(self):
        for cmd in ['ID?','FW?','SN?','TP?','WR?','WL?']:
            print self.sendcmd(cmd)

    def setWA(self, lmbda):
        return self.sendcmd('WL '+str(lmbda))

    def getWA(self):
        return self.sendcmd('WL?')


class wss(serialb):
    def __init__(self, COM_PORT,baudrate=115200,debuglevel=0):
        super(wss,self).__init__(COM_PORT,baudrate,debuglevel)

    def diag(self):
        for cmd in ['HWR?','FWR?','SNO?','MFD?','BLR?','NVR?', 'CAR?','OSS?','HSS?','LSS?','CSS?','ISS?']:
            print self.sendcmd(cmd)

    def rra(self):
        return self.sendcmd('rra?')

    def sab(self):
        return self.sendcmd('sab')

    def sfd(self):
        return self.sendcmd('sfd')

    def rsw(self):
        return self.sendcmd('rsw')

    def ura(self,ch,port,attn):
        return self.sendcmd('ura '+str(ch)+','+str(port)+','+str(attn))
