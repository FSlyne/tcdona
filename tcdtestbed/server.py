import pxssh
import re

class server(object):
    def __init__(self,server,username,password,sudo=True, opt=''):
       self.hostname=server
       self.username=username
       self.password=password
       self.handle=pxssh.pxssh()
       self.handle.login(self.hostname,self.username,self.password,opt=opt)
       if sudo:
          self.handle.sendline('sudo su -')
          self.handle.set_unique_prompt()
#       self.handle.prompt()

    def __del__(self):
       pass

    def sendcmd(self,line):
       self.handle.sendline(line)
       self.handle.prompt()
       return self.handle.before

    def sendcmdx(self,line):
       self.handle.sendline(line)
       return

    def logout(self):
       self.sendcmd('exit') # log out of 'sudo'
       self.handle.logout()
       
    def close(self):
        self.logout()
        
    def killProcess(self,process):
       self.sendcmd('kill -9 $(ps aux | grep \'' + process + '\' | grep -v grep | awk \'{print $2}\')')
       return self.sendcmd('pkill ' + process)

    def cd(self,directory):
       return self.sendcmd('cd ' + directory)

    def nohup(self,program):
       return self.sendcmd('nohup ' + program + ' &')
    
    def hardbounce(self):
        return self.sendcmd('shutdown -r now')

    def su(self, user):
        self.handle.sendline('su '+user)
        self.su_count = self.su_count + 1
        self.handle.set_unique_prompt()
        self.sendcmd('cd ~')
    
    def checkifRunning(self, proc):
        cmd = 'ps -ef | grep '+proc+' | grep -v grep | wc -l'
        line =  self.sendcmd(cmd)
        lines = line.split('\n')
        return lines[1]

    def checkIntStatus(self,iface):
        cmd='cat /sys/class/net/'+iface+'/operstate'
        line =self.sendcmd(cmd)
        if re.search(r'up',line,re.M|re.I):
           return True
        if re.search(r'down',line,re.M|re.I):
           return False
        return False
        

class tbserver(server):
    def __init__(self,servername):
        self.hostname=servername
        self.username=servername
        self.password='qwerty' + servername[-2:]
        super(tbserver,self).__init__(self.hostname,self.username,self.password)

class geantserver(server):
    def __init__(self,servername):
        self.hostname=servername
        self.username='root'
        self.password='discus'
        super(geantserver,self).__init__(self.hostname,self.username,self.password)

