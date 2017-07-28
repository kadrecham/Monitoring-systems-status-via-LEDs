from threading import Thread
import time
import sys
import os
import sqlite3
import urllib2, base64
import json
from neopixel import *
from influxdb import InfluxDBClient

LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

class State (object):
    
    def __init__(self):
        self.quit = 0
        self.up_colors = ['0, 0, 0' for k in range(LED_COUNT)]
        self.down_colors = ['0, 0, 0' for k in range(LED_COUNT)]
        self.blinks = [0 for k in range(LED_COUNT)]
        self.flag = [0 for k in range(LED_COUNT)]
        self.consumer_thread = Thread(target=self.run_LEDs)
        self.consumer_thread.deamon = True
        self.consumer_thread.start()

    def get_RGB_color(self, rgb):
        ls = rgb.split(',')
        return map(int,ls)

    def server_status(self, prox, host):
        if prox == 1:
            os.environ['NO_PROXY']= host
        try:
            responce = os.system("ping -c 1 -w 1 " + host)
            if responce == 0:
                return 1
            else:
                return 0
        except Exception as e:
            return 0
            print ("Can not make ping {}".format(e))

    def influx_status(self, prox, host, port, db, user, pswd, query):
        if prox == 1:
            os.environ['NO_PROXY']= host
        try:
            client = InfluxDBClient(host, port, db, user, pswd)
            result = client.query(query)
            if result.items():
                for r in result.get_points():
                    return r.get('last')
            else:
                return 0
        except Exception as e:
            return 0
            print ("Can not make Influx query {}".format(e))    
        
    def loadJSONFromURL(self, url, username, password):
        try:
            print("Executing the URL: " + url)
            request = urllib2.Request(url)
            base64string = base64.b64encode('%s:%s' % (username, password))
            request.add_header("Authorization", "Basic %s" % base64string)
            result = urllib2.urlopen(request, timeout=3)
            return json.load(result)
        except Exception as e:
            print ("Exception while requesting {}. {}".format(url, e))
            return None
        
    def grafana_status(self, prox, host, port, source, db, user, pswd, query):
        if prox == 1:
            os.environ['NO_PROXY']= host
        URL = "http://{}:{}/api/datasources/proxy/{}/query?db={}&q={}".format(host, port, source, db, query.replace(" ", "%20"))
        try:
            statusJSON = self.loadJSONFromURL(URL, user, pswd)
            status = statusJSON["results"][0]['series'][0]['values'][0][1]
            return status
        except Exception as e:
            print "JSON does not contain any result."
            print e
            return 0

    def connectdb(self, db):
        try:
            conn = sqlite3.connect(db)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(e)
            sys.exit()
          
    def read_database(self, db):
        conn = self.connectdb(db)
        while True:
            try:
                c = conn.cursor()
                self.quit = c.execute("select qFlag from quit").fetchone()[0]
                if self.quit == 1:
                    sys.exit()
                result = c.execute("select * from leds").fetchall()
                index = 0
                for row in result:
                    self.up_colors[index] = row['up_color']
                    self.down_colors[index] = row['down_color']
                    self.blinks[index] = row['blink']
                    if row['source']== 'Server':
                        self.flag[index] = self.server_status(row['proxy'], row['host'])
                    if row['source']=='InfluxDB':
                        self.flag[index] = self.influx_status(row['proxy'], row['host'], row['port'], row['dbName'], row['user'], row['password'], row['dbQuery'])
                    if row['source']=='Grafana':
                        self.flag[index] = self.grafana_status(row['proxy'], row['host'], row['port'], row['sourceID'], row['dbName'], row['user'], row['password'], row['dbQuery'])
                    index += 1
                time.sleep(5)
            except (KeyboardInterrupt, SystemExit):
                self.quit = 1
                print 'Stopping...'
                raise
            except Exception as e:
                print ("Can not read database {}".format(e))
                time.sleep(10)

    def reset_LEDs(self,strip):
        for i in range(strip.numPixels()):
            strip.setPixelColorRGB (i, 0, 0, 0)
        strip.show()
        
    def run_LEDs(self):
        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        strip.begin()
        toggle = False
        while True:
            if self.quit == 1:
                self.reset_LEDs(strip)
                print 'Turning off...'
                sys.exit()
            for i in range(strip.numPixels()):
                up_color = self.get_RGB_color(self.up_colors[i])
                down_color = self.get_RGB_color(self.down_colors[i])
                if self.flag[i] == 0:
                    if self.blinks[i] == True:
                        if toggle == True:
                            strip.setPixelColorRGB (i, down_color[0], down_color[1], down_color[2])
                        else:
                            strip.setPixelColorRGB (i, 0, 0, 0)
                    else:
                        strip.setPixelColorRGB (i, down_color[0], down_color[1], down_color[2])
                else:
                    strip.setPixelColorRGB (i, up_color[0], up_color[1], up_color[2])
            strip.show()        
            toggle = not toggle
            time.sleep(0.5)
        self.quit == 1
            
if __name__ == '__main__':
    
    state = State()
    state.read_database('config')
