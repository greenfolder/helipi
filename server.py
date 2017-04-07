import os
import socket
from thread import *
import struct
from Adafruit_PWM_Servo_Driver import PWM
import time
from array import array
import smbus
import math

#This runs on the pi
#What this does
# 1) creates a pygame window
# 2) creates a udp socket
# 3) listens for incoming data
# 4) unpacks the data which is sent in X X X X X format, where X is a number
# 5) plugs values into servos and the motor


##PYGAME WINDOW - draw etc###

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_name=''
server_port=5555

try:
	s.bind((server_name, server_port))

except socket.error as e:
	print (str(e))

s.listen(5)

print ('waiting for a connection')


                
########

####Servo stuff from adafuit I think
pwm = PWM(0x40)

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 50                       # 60 Hz
  print ("%d us per period" % pulseLength)
  pulseLength /= 4096                     # 12 bits of resolution
  print ("%d us per bit" % pulseLength)
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

pwm.setPWMFreq(50)                        # Set frequency to 60 Hz

####get compass, gyro readings. convert, print out####

def threaded_client(conn):
        
        while True:
       

                unpacker=struct.Struct('I I I I I')
                data=conn.recv(unpacker.size)
                data=unpacker.unpack(data)
                
                x=int(data[0])
                z=int(data[1])
                r=int(data[2])
                u=int(data[3])
                p=int(data[4])

                pwm.setPWM(14,0, x)  ##min
				        pwm.setPWM(12,0, z)  ##min
                pwm.setPWM(13,0, r)  ##min
                pwm.setPWM(15,0, u)
                pwm.setPWM(0, 0, p)
                #time.sleep(0.01)

                
                print ((x,z,r,u,p))

                #print (str(addr) + 'connected')
                #print (str(addr) + " says: "+(data))


### THE LINE BELOW DOESN'T SEEM TO WORK
                if not data:
                        pwm.setPWM(0, 0, 0)
                        break
### THE LINE ABOVE DOESN'T SEEM TO WORK
### This is where I want to set the motor 0 - off - should I lose connection, but it's not working

        conn.close()
while True:
        conn, addr=s.accept()
        start_new_thread(threaded_client, (conn, ))        
        print (str(addr) + ' connected')

