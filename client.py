import os
import socket
from _thread import *
import pygame
import atexit
import struct
from array import array
import time

#what this all does
# 1) starts pygame and draws a window
# 2) creates a udp socket 
# 3) defines starting positions for servos and ESC
# 4) finds and initializes a joystick
# 5) assigns joystick axis and buttons to servos and motor
# 6) looks for joystick motions and adjusts servo and motor positions accordingly
#### all controlled via this: 
#### https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi/overview

#1 start pygame and draw a window

pygame.init()

WINDOW = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('fly-by-wire')
myfont=pygame.font.SysFont("monospace", 15)

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

WINDOW.fill(WHITE)

#2 create a socket

print ('creating a socket')

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_name='192.168.1.104'
server_port=5555

print ('socket created successfully')

print ('connecting...')

s.connect((server_name, server_port))
print ('connected')


#except socket.error as e:
#	print (str(e))

#s.listen(5)

print ('waiting for a connection')

# 3 define starting/neutral/middle positions for servos and ESC (Electronic speed contorller)

ESCinit=220
ESCMin=240
ESCMax=570


servoElMax=435 		##14
servoElMin=240
servoElMid=365

servoPitchMin = 240  	##12 	#Min pulse length out of 4096
servoPitchMax = 435  	# 		#Max pulse length out of 4096
servoPitchMid = 325

servoRollMin = 240  	#### 13
servoRollMax=435
servoRollMid=365

servoTailMin=245
servoTailMid=305
servoTailMax=438

#4 find and initiliaze a joystick 

try:
	j=pygame.joystick.Joystick(0)
	j.init()
	print ("Joystick %s online" %j.get_name())

except pygame.error:
	print ("where is the joystick?")
	quit()



done=False 



#5 assign joystick axis and buttons to servos and motor


while done==False:
        for event in pygame.event.get():

           
				
		cc=j.get_axis(1) # 12 pitch forwards backwards
                bb=j.get_axis(0) # 13 roll, left right
                dd=j.get_axis(2) # 14 elevator, slider
                aa=j.get_axis(3) # 15 tail, z axis

                b0=j.get_button(0) #trigger - tail right                
                b1=j.get_button(1) # 1, tail left               
                b2=j.get_button(2) # 2, pitch up               
                b3=j.get_button(3) # 3, roll up               
                b4=j.get_button(4) # 4, pitch down               
                b5=j.get_button(5) # 5, roll down               
                b6=j.get_button(6) # 6, front, ???                

                
      
                if event.type==pygame.QUIT:
                        done=True

                ## TAIL TRIM
                if b0==1:
                        servoTailMid=servoTailMid+2
                if b1==1:
                        servoTailMid=servoTailMid-2

                #ELEVATOR TRIM

                if event.type==pygame.KEYDOWN and event.key==pygame.K_q:
                        servoElMid=servoElMid+2
                if event.type==pygame.KEYDOWN and event.key==pygame.K_w:
                        servoElMid=servoElMid-2

                #PITCH TRIM
                if b2==1:
                        servoPitchMid=servoPitchMid+2
                if b4==1:
                        servoPitchMid=servoPitchMid-2

                # ROLL TRIM

                if b3==1:
                        servoRollMid=servoRollMid-2
                if b5==1:
                        servoRollMid=servoRollMid+2

                

#6 what to do when joystick stick changes position - a.k.a. the control centre                

                if event.type==pygame.JOYAXISMOTION:


			
                        


                        if aa<=0:
                                
                                u=int(((aa/(-(32768/(servoTailMax-servoTailMid)))*32768)))+servoTailMid
                                
                        if aa>=0:
                                u=servoTailMid-int(((aa/(32768/(servoTailMid-servoTailMin)))*32768))
#######
##UP AND DOWN ALL SERVOS - SLIDER - MAIN POSITION AND THRUST CONTROL
#######

###UP ALL 3 SERVOS
                        if dd<=0:

                                x = int(servoElMid-(int((int(dd*32768)/(-32768/(servoElMid-servoElMin))))))
                                z = int((int(((dd/-(32768/(servoPitchMax-servoPitchMid))*32768))))+servoPitchMid) 
                                r = int(servoRollMid-(int((int(dd*32768)/(-32768/(servoRollMid-servoRollMin))))))
                               
                                p= int(405+int(((-dd/0.006))))
                               
                                data=(x, z, r, u, p)
                                                            
                        if dd>=0:
                                x = servoElMid+(int((int(dd*32768)/(32768/(servoElMax-servoElMid))))) 
                                z = servoPitchMid-(int(((dd/(32768/(servoPitchMid-servoPitchMin))*32768))))
                                r = servoRollMid+(int((int(dd*32768)/(32768/(servoRollMax-servoRollMid)))))
                                p=405-int((dd/0.006))

                                data=(x, z, r, u, p)
#SERVO 12 and 13 LEFT AND RIGHT 
                        
######## ROLL

#LEFT
                                
                        if bb<=0:
                                z=z-(int(((-bb/(32768/((z-servoPitchMin))*32768)))))
                                r=(r-(int(-bb*32768)/(32768))/(r-servoRollMin))
								
                                data=(x, z, r, u, p)
                                

##RIGHT
                        if bb>=0:
                                z = (z + (int((((bb/(32768/(servoPitchMax-z))*32768))))))
                                r = r +(int((((bb*32768)/(32768/(servoRollMax-r))))))

                                data=(x, z, r, u, p)
                                
##### PITCH 

### BACKWARDS

                        if cc>=0:
                                x= int(x+int((x*(cc/10))))
                                z = z+int((int(((cc/(32768/(servoPitchMax-z))*32768))))) #12 #UP
                                r = (r-int(((cc*32768/(32768/(r-servoRollMin))))))
                                
                                data=(x, z, r, u, p)

### FORWARD

                        if cc<=0:
                                x=x-int(x*(-cc/10))
                                z = z-int((int((((-cc/(32768/(((z-servoPitchMin))*32768)))))))) #12 #down
                                r = r+(int(((cc*32768)/(-32768/(servoRollMax-r)))))

                                data=(x, z, r, u, p)
                                

                        print ((data))
                        packer=struct.Struct('I I I I I')
                        packed_data=packer.pack(*data)
                        s.send(packed_data)
                        time.sleep(0.01)

                        
