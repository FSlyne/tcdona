
class itugrid():
   def __init__(self):
      file='/usr/local/lib/python2.7/dist-packages/ona/itugrid.map'
      with open(file) as fin:
         rows = ( line.rstrip('\n').split('\t') for line in fin )
         self.d = { row[0]:row[1:] for row in rows }

   def fpga(self,itu):
      itu=str(itu)
      fpgax,fpga,wss,thz,nm,itu = self.d[itu]
      return fpga

   def wss(self,itu):
      itu=str(itu)
      fpgax,fpga,wss,thz,nm,itu = self.d[itu]
      return wss

   def thz(self,itu):
      itu=str(itu)
      fpgax,fpga,wss,thz,nm,itu = self.d[itu]
      return thz

   def nm(self,itu):
      itu=str(itu)
      fpgax,fpga,wss,thz,nm,itu = self.d[itu]
      return nm
