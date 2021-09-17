#Libraries
import time
import datetime
import sys
import subprocess

from pinform import Measurement
from pinform.fields import FloatField
from pinform.tags import Tag
from pinform.client import InfluxClient



class OHLC(Measurement):
  class Meta:
    measurement_name = 'grid'

  symbol = Tag(null=False)
  W = FloatField(null=False)

cli = InfluxClient(host="localhost", port=8086, database_name="el", username='myuser', password='mypassword')


sample_time = 60.0  # Second interval to report to database

w_sum = 0
samples = 0

last_time =  time.time()


while 1 == 1:
    now = time.time()
    if now > last_time + sample_time:
        w = w_sum/samples
        w_sum = 0
        if w > 0:
            current_growatt = OHLC(time_point=datetime.datetime.utcnow(), symbol='growatt', W=w) 
            cli.save_points([current_growatt]) 
#        print(time.time(),samples,w)
        samples = 0
        last_time = now


    # just sample once per second and do average 
    try:
        w_now = float( subprocess.getoutput("~/modpoll/linux_arm-eabihf/modpoll -m rtu -a 1 -r 1 -c 125 -t 3 -1 -4 10 -p none -b 9600 /dev/ttyUSB0 | sed -n '52p' | awk '{print $2}'")  )/10.0
    except:   # if inverter is switched off or does not answer
        w_now = 0

    w_sum += w_now
    samples += 1
    time.sleep(1)
       

