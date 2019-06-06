Pi Weather Station
==================

This is a Raspberry Pi project that measures weather values (temperature, humidity and pressure) using the Astro Pi Sense HAT then uploads the data to a Weather Underground weather station. The Sense HAT board includes instruments that measure temperature, humidity and barometric pressure plus an 8x8 LED display, a joystick, and an accelerometer.  The HAT was created by the folks at [Astro Pi](https://astro-pi.org/); elementary school children were solicited to create experiments using the Sense HAT it that would be executed on the International Space Station. Eventually, many experiments were selected and an astronaut performed them and sent back the results for analysis. I read different articles about this board, so I decided to create a project using it. I'd wanted to install a weather station in my yard and upload the weather data to [Weather Underground](www.weatherunderground.com); the Sense HAT and a Raspberry Pi seemed like a great way to do this.

Note: If you'd like to display one of the measurements on the display instead of the arrows this app uses, take a look at this: [http://yaab-arduino.blogspot.co.uk/2016/08/display-two-digits-numbers-on-raspberry.html](http://yaab-arduino.blogspot.co.uk/2016/08/display-two-digits-numbers-on-raspberry.html). 
 
Required Components
===================

This project is very easy to assemble, all you need is the following 4 parts, and they all connect together:

+ [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) - I selected this model because it has built in Wi-Fi capabilities. You can use one of the other models, but you'll need to also purchase a Wi-Fi module or run the device on a wired connection.
+ [Astro Pi Sense HAT](https://www.adafruit.com/product/2738). There was a bad batch of Sense HAT device out there, so be careful. See the note below.
+ Raspberry Pi case. The only commercial case I could find that supports the Sense HAT is the [Zebra Case](http://c4labs.net/collections/all/zebra-case) from C4 Labs with the [Official Sense HAT upgrade for Zebra Case](http://c4labs.net/products/official-sense-hat-upgrade-for-zebra-case). You can also 3D print a case, you can find plans here: [http://www.thingiverse.com/thing:1200534](http://www.thingiverse.com/thing:1200534).
+ Raspberry Pi Power Adapter. I used this one from [Amazon](http://amzn.to/29VVzT4). 

**Note:** *When I started this project, there were quite a few companies selling Sense HAT devices, but very few of them had stock available. I finally found I could purchase one of the through Amazon.com, but when I plugged everything together and ran my code, I got results that didn't make sense. After sending that board back and getting another one with the same problem, I discovered it wasn't my code at fault. It turns out that Astro Pi used some faulty components in a batch of them and had to fix that problem before shipping any more. Refer to [Defective Astro Pi Sense HAT Boards](http://johnwargo.com/index.php/microcontrollers-single-board-computers/defective-astro-pi-sense-hat-boards.html) for more information about the faulty Sense HAT boards.*

Project Files
=============

The project folder contains several files and one folder: 

+ `LICENSE` - The license file for this project
+ `readme.md` - This file. 
+ `weather_station_ubi.py` - The main data collection application for this project. You'll run this application to read the Sense HAT board and post the collected data.   

Hardware Assembly
=================

Assembly is easy - mount the Sense HAT on the Raspberry Pi then insert it in the case and plug it into power. All set! No wiring, soldering or anything else required.

**Note:** *The Raspberry Pi foundation recommend you mount the Sense HAT to the Raspberry Pi using [standoffs](http://www.mouser.com/Electromechanical/Hardware/Standoffs-Spacers/_/N-aictf) and the Sense HAT I purchased included them in the package. Unfortunately, standoffs are incompatible with the C4 Labs Zebra Case and their Official Sense HAT upgrade for Zebra Case. Be sure to omit standoffs if using this case.*

Installation
============

Download the Raspbian image from [raspberrypi.org](https://www.raspberrypi.org/downloads/raspbian/) then burn it to an SD card using the instructions found at [Installing Operating System Images](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).

Power up the Raspberry Pi. If you'll be using a Wi-Fi connection for your Pi, configure Wi-Fi access using [Wi-Fi](https://www.raspberrypi.org/documentation/configuration/wireless/).

Next, open a terminal window and execute the following commands:

	sudo apt-get update
	sudo apt-get upgrade
	sudo pip install ubidots==1.6.6
	
Those 3 commands will update the Pi's software repository with the latest information then upgrade existing code in the Raspbian image for the latest versions and add a Ubidots library

Next, you'll need to install support packages for the Sense HAT. In the same terminal window, execute the following command:

    sudo apt-get install sense-hat
	   
Installation
============

Make a folder in the pi user's home folder. to do this, open a terminal window and enter the following command:
 
	mkdir folder_name

For example: 

	mkdir pisensehat

Copy the project files into the folder that was just created.

Configuration
=============

The main application file, `weather_station_ubi.py` has two configuration settings that control how the program operates. Open the file in your favorite text editor and look for the following line near the beginning of the file:

	# specifies how often to measure values from the Sense HAT (in minutes)
	MEASUREMENT_INTERVAL = 10  # minutes

The `MEASUREMENT_INTERVAL` variable controls how often the application reads temperature measurements from the Sense HAT. To change how often the application checks temperature values, change the value on the right of the equals sign on the second line.

Testing the Application
=======================
  
To execute the data collection application, open a terminal window, navigate to the folder where you copied the project files and execute the following command: 

	sudo python weather_station_ubi.py

The terminal window should quickly sprout the following output:

	Initializing the Sense HAT client	
	Initialization complete!
	ecc ecc
 
If you see something like that, you're golden. If not, figure out what any error messages mean, fix things, then try again. At this point, the application will start collecting data and uploading it to the Weather Underground every 10 minutes on the 10 minute mark (unless you changed the app's configuration to make the application work differently).

Starting The Project's Application's Automatically
--------------------------------------------------
sudo nano crontab -e

add this line:
@reboot python /home/pi/pisensehat/weather_station_uby.py &
