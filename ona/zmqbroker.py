import threading
import zmq
import time
import datetime
import sys

def threaded(fn):
    def wrapper(*args, **kwargs):
        t=threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.daemon=True
        t.start()
    return wrapper


def mstime():
  t=datetime.datetime.now()
  return t.strftime('%s.%%06d') % t.microsecond

class zmqBroker(object):
  def __init__(self,brokerport=10001,pubsubport=10000):
     self.brokerport=brokerport
     self.pubsubport=pubsubport
     self.context=zmq.Context()
     self.broker=self.context.socket(zmq.REP)
     self.pubsub=self.context.socket(zmq.PUB)
     self.broker.bind("tcp://*:%s" % self.brokerport)
     self.pubsub.bind("tcp://*:%s" % self.pubsubport)
     self.debug=0
     self.worker()

  @threaded
  def worker(self):
     while True:
       #  Wait for next request from client
       message = self.broker.recv()
       self.pubsub.send(message)
       self.broker.send('')
       if self.debug>0: 
         print message

class zmqSender(object):
  def __init__(self,category="Category",brokerhost='localhost',brokerport=10001):
    self.brokerhost=brokerhost
    self.brokerport=brokerport
    self.category=category
    self.context=zmq.Context()
    self.broker=self.context.socket(zmq.REQ)
    print self.broker.connect ("tcp://%s:%s" % (self.brokerhost,self.brokerport))

  def tx(self,msg="Null Message"):
    try:
      self.broker.send ("%s %s %s" % (self.category,mstime(),msg) )
      self.broker.recv()
    except:
      print "zmq tx error"

class zmqSubscriber(object):
  def __init__(self,category="Category",pubsubhost='localhost',pubsubport=10000):
    self.pubsubhost=pubsubhost
    self.pubsubport=pubsubport
    self.category=category
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect ("tcp://%s:%s" % (self.pubsubhost,self.pubsubport))
    self.socket.setsockopt(zmq.SUBSCRIBE, self.category)
    self.worker()

  @threaded
  def worker(self):
    while True:
      message = self.socket.recv()
      (category,sendtime,msg)=message.split()
      rcvtime=mstime()
      self.process(rcvtime,message)

  def process(self,mst,message):
      print "%s Message %s" % (mst,message)
