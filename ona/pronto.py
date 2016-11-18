from tcdtestbed.server import *

class Pronto(server):
    def __init__(self,server):
        self.hostname=server
        self.username='root'
        self.password='pica8'
        super(Pronto,self).__init__(self.hostname,self.username,self.password)
        self.THISMACHINE = server
        self.OVS_PORT = 6633
        self.DEBUG = 0
        self.BRIDGES = []
        
    def __del__(self):
      super(Pronto,self).__del__()

    def resetOVS(self,OVS_PORT,SFLOW_PORT,hard):
        self.OVS_PORT = OVS_PORT
        self.SFLOW_PORT = SFLOW_PORT
        if hard>0:
           self.killOVS()
           self.clearOVSDB()
           self.createOVS(OVS_PORT,SFLOW_PORT)
           return
        ovsdb_count = self.checkifRunning('ovsdb-server')
        ovs_count= self.checkifRunning('ovs-vswitchd ')
        print "OVSDB Count = %s, OVS Switch Count = %s" % (str(ovsdb_count), str(ovs_count))
        if ovs_count == 0:
           self.killOVS()
           self.clearOVSDB()
           self.createOVS(OVS_PORT,SFLOW_PORT)
        elif ovs_count > 2 or ovsdb_count > 1:
           self.killOVS()
           self.createOVS(OVS_PORT,SFLOW_PORT)
        elif ovsdb_count == 1:
           self.clearOVS()
        elif ovsdb_count == 0:
           self.startOVSDB(OVS_PORT,SFLOW_PORT)
      
    def createOVS(self,OVS_PORT,SFLOW_PORT):
        self.OVS_PORT = OVS_PORT
        self.SFLOW_PORT = SFLOW_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovsdb-tool create /ovs/ovs-vswitchd.conf.db /ovs/share/openvswitch/vswitch.ovsschema')
        self.sendcmd('ovsdb-server /ovs/ovs-vswitchd.conf.db --remote=ptcp:'+str(OVS_PORT)+':'+THISMACHINE+' &')
        self.sendcmd('ovs-vswitchd tcp:'+THISMACHINE+':'+str(OVS_PORT)+' --pidfile=pica8 --overwrite-pidfile > /var/log/ovs.log 2>/dev/null &')
        
    def startOVSDB(self,OVS_PORT,SFLOW_PORT):
        self.OVS_PORT = OVS_PORT
        self.SFLOW_PORT = SFLOW_PORT
        THISMACHINE = self.THISMACHINE        
        self.sendcmd('ovsdb-server /ovs/ovs-vswitchd.conf.db --remote=ptcp:'+str(OVS_PORT)+':'+THISMACHINE+' &')
        
    def killOVS(self):
#        for bridge in self.BridgeArray:
#            self.delDefFlows(bridge)
        self.sendcmd('pkill ovs-vswitchd')
        self.sendcmd('pkill ovsdb-server')
        
    def clearOVS(self):
        for b in range(0,1):
            self.delBridge(b)
            
    def clearOVSDB(self):
        self.cd('/ovs')
        self.sendcmd('rm /ovs/ovs-vswitchd.conf.db')
    
# ========================= Add Bridges and Ports ======================

    def addBridge(self,bridge):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'+str(OVS_PORT)+ 
			' add-br br'+str(bridge)+' -- set bridge br'+str(bridge)+' datapath_type=pica8')

    def delBridge(self,bridge):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'+str(OVS_PORT)+' --if-exists del-br br'+bridge)
        
    def addPortBridge(self,bridge,port):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'+str(OVS_PORT)+
                ' add-port br'+str(bridge)+' te-1/1/'+str(port)+' -- set interface te-1/1/'+str(port)+' type=pica8')
            
    def addPortBridgeAuto(self,bridge,port):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'+str(OVS_PORT)+' add-port br'+
		bridge+' te-1/1/'+str(port)+' vlan_mode=trunk tag=1 trunks=10,20 -- set interface te-1/1/'+
			str(port)+' type=pica8  options:link_speed=auto')
            
            
    def addPortBridge10G(self,bridge,port):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'+str(OVS_PORT)+' add-port br'+str(bridge)+' te-1/1/'+str(port)+' -- set interface te-1/1/'+str(port)+' type=pica8  options:link_speed=10G')

    def delPortBridge(self,bridge,port):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'+str(OVS_PORT)+' --if-exists del-port br'+str(bridge)+' te-1/1/'+str(port))
            
    def delDefFlows(self,bridge):
        self.sendcmd('ovs-ofctl del-flows br'+str(bridge))
        
    def connectBridgeController(self,bridge,controller,controller_port):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        SFLOW_COLLECTOR = '10.10.10.5';
        SFLOW_PORT = self.SFLOW_PORT
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'+
                     str(OVS_PORT)+' set-controller br'+str(bridge)+' tcp:'+controller+':'+str(controller_port))
        self.sendcmd('ovs-vsctl --db=tcp:'+THISMACHINE+':'
                     +str(OVS_PORT)+' -- --id=@s create sFlow agent=eth0 target=\"'+SFLOW_COLLECTOR+':'+
                            str(SFLOW_PORT)+'\" header=128 sampling=64 polling=10 -- set Bridge br'+str(bridge)+' sflow=@s')
        
        
    def addFlow(self,bridge,flow):
        self.sendcmd('ovs-ofctl add-flow br'+str(bridge)+' '+flow+';')
        
    def delFlow(self,bridgelist):
        for bridge in bridgelist:
            self.sendcmd('ovs-ofctl del-flows br'+str(bridge));
            
    def delSFlow(self,bridge):
        OVS_PORT = self.OVS_PORT
        THISMACHINE = self.THISMACHINE
        self.sendcmd('ovs-ofctl --db=tcp:'+THISMACHINE+':'+str(OVS_PORT)+' -- clear Bridge br'+str(bridge)+' sflow')

    def addMeterDrop(self,bridge, meter, rate, burst):
        line = 'ovs-ofctl add-meter br'+bridge+' meter_id='+meter+',flags=KBPS,band=type:drop,rate:'+rate
        if (burst):
            line = 'ovs-ofctl add-meter br'+bridge+' meter_id='+meter+',flags=KBPS/BURST,band=type:drop,rate:'+rate+',burst_size='+burst
        self.sendcmd(line)
        
    def addMeterDscpMark(self, bridge,meter, rate, preclevel, burst):
        line = 'ovs-ofctl add-meter br'+bridge+' meter_id='+meter+',flags=KBPS,band=type:dscp_remark,rate:'+rate+',prec_level='+preclevel
        if (burst):
            line = 'ovs-ofctl add-meter br'+bridge+' meter_id='+meter+',flags=KBPS/BURST,band=type:dscp_remark,rate:'+rate+',prec_level='+preclevel+',burst_size='+burst
        self.sendcmd(line)

    def modMeterDrop(self,bridge, meter, rate, burst):
        line = 'ovs-ofctl mod-meter br'+bridge+' meter_id='+meter+',flags=KBPS,band=type:drop,rate:'+rate
        if (burst):
            line = 'ovs-ofctl mod-meter br'+bridge+' meter_id='+meter+',flags=KBPS/BURST,band=type:drop,rate:'+rate+',burst_size='+burst
        self.sendcmd(line)
        
        
    def modMeterDscpMark(self, bridge,meter, rate, preclevel, burst):
        line = 'ovs-ofctl mod-meter br'+bridge+' meter_id='+meter+',flags=KBPS,band=type:dscp_remark,rate:'+rate+',prec_level='+preclevel
        if (burst):
            line = 'ovs-ofctl mod-meter br'+bridge+' meter_id='+meter+',flags=KBPS/BURST,band=type:dscp_remark,rate:'+rate+',prec_level='+preclevel+',burst_size='+burst
        self.sendcmd(line)
        
    def delMeter(self,bridge, meter):
        if (meter):
            self.sendcmd('ovs-ofctl del-meter br'+bridge+' meter_id='+meter)
        else:
            self.sendcmd('ovs-ofctl del-meter br'+bridge)
        
