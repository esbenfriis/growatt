#Libraries
import RPi.GPIO as GPIO
import time
import datetime
import sys

from pinform import Measurement
from pinform.fields import FloatField
from pinform.tags import Tag
from pinform.client import InfluxClient


class OHLC(Measurement):
  class Meta:
    measurement_name = 'grid'

  symbol = Tag(null=False)
  Wh = FloatField(null=False)
  W = FloatField(null=False)

cli = InfluxClient(host="localhost", port=8086, database_name="el", username='myuser', password='mypassword')


#Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#Set Button and LED pins
Button =  13

#Setup Button and LED
GPIO.setup(Button,GPIO.IN,pull_up_down=GPIO.PUD_UP)

#flag = 0
button_state = 1
ldr=1

flashmin  =  100   #  number of reads "0" of the LDR GPIO pin to determine a flash 
pausemin = 400     #  number of reads "1" of the LDR GPIO pin to determine no flash
flash = 0   # flash count
led = False   # led state
pause = True

sample_time = 60.0  # Second interval to count flashes   
detect = 0

build = [0,pausemin+1]  # build is led[on,off]
last_time =  time.time()

while 1 == 1:
    now = time.time()
    if now > last_time + sample_time:
        w = round(float(flash))*3600.0/sample_time     
        current_grid = OHLC(time_point=datetime.datetime.utcnow(), symbol='maaler', Wh=flash, W=w) 
        cli.save_points([current_grid]) 
#        print(time.time(),flash,w)

        flash = 0
        
        last_time = now

    ldr = GPIO.input(Button)
    detect = detect - ldr + int(ldr==0)   # +1 for on, -1 for off
    if detect < -pausemin:
       pause = True     
       led=False
       detect=0

    if detect > flashmin:    
       led=True
       detect=0

    if led and pause:
       flash += 1
       pause = False
 

