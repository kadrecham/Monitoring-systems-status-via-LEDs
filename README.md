# Monitoring-of-systems-status-via-LEDs
## Using LEDs to monitor and visualize the status (UP-DOWN) of the systems 

### Summary:
This system queries the status of the systems and drives a LED strip depending on the results of this query.    

![alt tag](https://user-images.githubusercontent.com/25906706/28717277-67d1fb68-73a1-11e7-89c2-a494f6e1f116.jpeg)

### Tools:
* [Raspberry Pi3 Model:B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) with [Raspbian operating system](https://www.raspbian.org/)
* [NeoPixels WS2811/WS2812 LEDs strip](https://www.adafruit.com/product/2837)
* Python 2.7+
* [rpi_ws281x Library](https://github.com/jgarff/rpi_ws281x.git)
* [Python client for InfluxDB](https://github.com/influxdata/influxdb-python)

### Hardware setup:
* Connect the *NeoPixels LEDs strip* to work with the *Raspberry Pi* by following the instructions from [HERE](https://learn.adafruit.com/neopixels-on-raspberry-pi/wiring).
* Disable the on-board audio by [blacklisting the Broadcom audio kernel modules](http://www.instructables.com/id/Disable-the-Built-in-Sound-Card-of-Raspberry-Pi/), to avoid random LEDs flickering. More information from [HERE](https://github.com/jgarff/rpi_ws281x/wiki)

### Software setup:
* Install the rpi_ws281x Library by following the instructions [HERE](https://learn.adafruit.com/neopixels-on-raspberry-pi/software)
* Install the Python client for InfluxDB from [HERE](https://github.com/influxdata/influxdb-python#installation)
* Clone the **gui_application** and the **leds_driver** python files from [HERE](https://github.wdf.sap.corp/D069020/Monitoring-of-systems-status-via-LEDs) to the same directory

### Using apllication:
* Run the apllication:  `$ python gui_application.py`
* Select the LED number, the UP and DOWN state colors and the datasources. You can choose between three type of data sources (Grafana, Influxdb, Server(ping))
* Add the host address, port number, source ID (only when you use Grafana as data sources), database name, username, password and the query. In case you want to use ping to get the status of the server enter the host address only!
* Save the previous data for each LED
* Press **Start** button to run the LEDs according to your configurations
* Press **Stop** button to turn off the LEDs


### Notes:
* The application generates database file called **config** where all user inputs are stored. 
