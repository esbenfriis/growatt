import subprocess
import time
import datetime
import pandas as pd
from io import StringIO
from pinform import Measurement
from pinform.fields import FloatField
from pinform.tags import Tag
from pinform.client import InfluxClient

def price_table(area="DK2", currency_factor=0.00744):  

    # currency is the factor to go from EUR/MWh to <your currency>/KWh
    # Area is your geographical area of interest

    # cmdstr = "/usr/bin/chromium-browser --headless --disable-gpu --dump-dom 'https://www.nordpoolgroup.com/Market-data1/Dayahead/Area-Prices/DK/Hourly/?dd="+area+"&view=table' | html2text -width 200 | grep -A 26  'Last update' | sed -n '2,26p'"

    cmdstr = "/usr/bin/chromium-browser --headless --disable-gpu --dump-dom 'https://www.nordpoolgroup.com/Market-data1/Dayahead/Area-Prices/DK/Hourly/?dd="+area+"&view=table' | html2text -width 200 | grep -A 26 'EUR/MWh' | sed -n '3,27p'"
    print(cmdstr)
    raw_table = subprocess.check_output(cmdstr,shell=True).decode("utf-8")
    # f=open("price.txt")
    # raw_table = f.read()
    # f.close()

    df = pd.read_csv(StringIO(raw_table),sep='\s+',decimal=',',na_values='-')

    df.rename(columns = {df.columns[0]:'hour'}, inplace = True)

    print(df.shape)

    long = df.melt(id_vars='hour')
    long = long.dropna()
    long['time'] =  long['variable'].str.replace(r'(..)-(..)-(....)',r'\3-\2-\1') +"T"+ long['hour'].str.replace(".-...$",":00:00")
    long['price'] = long['value'] * currency_factor

    long['datetime'] = long['time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'))
   
    return long[['datetime','price']]

def prices2influx(prices):
    # prices is a df with at lest the columns ['datetime','price']
    # col datetime is in datetime format

    class OHLC(Measurement):
        class Meta:
            measurement_name = 'price'

        symbol = Tag(null=False)
        price = FloatField(null=False)

    cli = InfluxClient(host="localhost", port=8086, database_name="el", username='myuser', password='mypassword')

    prices['ohlc'] = prices.apply(lambda x: OHLC(time_point=x['datetime'], symbol='market', price=x['price']  ),axis=1)
    cli.save_points(prices['ohlc'].tolist())



prices2influx(price_table())

