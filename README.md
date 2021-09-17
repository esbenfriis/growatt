# growatt
## A small project to monitor and record data from
  * Growatt MIC 3000TL-X inverter  
  * Kamstrup power meter using its built-in LED (1 flash per Wh)
  * Nordpool hourly electricity price
  
using a Raspberry Pi 3B+

## Detailed notes from the installation


Install Raspbian OS (release 2021-01-11) using the raspberry imager  
The full installation (GUI + recommended programs) was used here   

### Log in to the Rapsberry
```
sudo adduser epf  # add user epf with default options
sudo adduser share   # add user share with default options
```

If you want a static IP (recommended), uncomment the static IP block in /etc/dhcpcd.conf:
```
interface eth0
static ip_address=192.168.1.2/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```
And reboot to make the changes take effect.  
Login as your newly created user (or pi, if you want to use that)  

Install grafana using this tutorial:  
https://pimylifeup.com/raspberry-pi-grafana/
```
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```
login to the Grafana interface:  http://<ip address>:3000  
login with  
```  
admin
admin
```
and change the admin password at the first login

Install Influxdb using this tutorial:   
https://pimylifeup.com/raspberry-pi-influxdb/
```  
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt update
sudo apt install influxdb
sudo systemctl unmask influxdb
sudo systemctl enable influxdb
```

Start the influx interface and create your database
```
influx
CREATE DATABASE el
exit
```

Download and install the modpoll serial driver (only necessary for Growatt support)  
```
wget https://www.modbusdriver.com/downloads/modpoll.tgz
tar -zxvf modpoll.tgz
``` 

Now create/copy the scripts for the grid and growatt survelliance
```
mkdir grid
# Copy and create the two scripts
grid/ldr_monitor.py
grid/growatt_monitor.py
```
Install the necessary libraries and python modules
```
sudo apt install libatlas-base-dev
sudo pip3 install pinform
sudo pip3 install pandas
sudo pip3 install influxdb
sudo pip3 install rfc3339
```
If you are not running as user "pi", you must add your user to the gpio and dialout groups. Edit the /etc/group file, to look like e.g.  
```
dialout:x:20:pi,epf
gpio:x:997:pi,epf
```
(I had to log out and back in for this to take effect)

```  
cd ~
```
  
Verify that the scripts run by starting them manually one by one.
```
python3 grid/ldr_monitor.py
python3 grid/growatt_monitor.py
```
Correct behaviour is that no output or error messages is produced :-)  

Make them start automatically on boot by adding these two lines to the crontab. Use "crontab -e" to edit the crontab
```  
@reboot python3 /home/epf/grid/ldr_monitor.py
@reboot python3 /home/epf/grid/growatt_monitor.py
05 01 * * *  /home/epf/grid/price_monitor.py
```
Reboot and make sure the scripts start

Check that some values are written to the influx database:
```
influx
use el
select * from grid
```
some output like this should be shown
```
time                W                  Wh symbol
----                -                  -- ------
1613480238704500000 480                8  maaler
1613480239720732000 22.889189189189192    growatt
1613480298704509000 540                9  maaler
1613480300465727000 22.525000000000002    growatt
```
```  
exit
```
  
Setting up Grafana  
Log into grafana GUI (http://<ip address>:3000) with your admin account (see above)  

Add a new data source from the GUI:  
Configuration -> Data sources -> Add data source -> influxDB  
Two fields must be configured:  
```  
URL: http://localhost:8086/  # with the trailing slash!!!!
database: el
```
  
Click the "Save & test" button

Create the Dashboard from the JSON file in the repos:

Create -> Import -> Upload JSON file 
select the "elpris.json" file and click import
 
