import socket

s = socket.socket()
s.connect(("192.168.1.251", 5025))

s.send("*IDN?\n")
print s.recv(4096)

s.send("i7; volt:rang:auto off\n")
s.send("i7; volt:rang ?\n")
print s.recv(4096)

s.send("i7; meas:volt ?\n")
print s.recv(4096)

import biltsocket as bs
b = bs.BiltSource()
print b.getcurrent(37)

print b.getvoltrange(37)
b.setvoltrange(37,1.2)
print b.getvoltrange(37)

print b.getcurrentrange(37)
b.setcurrentrange(37,0.2)
print b.getcurrentrange(37)

print b.getstatus(3)
print b.getvoltrange(3)
print b.getvoltage(3)
b.on(3)
print b.getstatus(3)
b.off(3)
print b.getstatus(3)
