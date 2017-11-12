# Hideki TS33C Wireless Temperature/Humidity Sensor
Analysis and decoding of temperatures and humidity values sent by this wireless sensor.

# Technical Specifications

Item | Value | Description
-------------: | ------------- | :-------------
Frequency  | 433.964MHz | GeoJSON-Object to draw as geodesic-lines.

# Decoding Tool
Use the [rtl_433-tool](https://github.com/merbanan/rtl_433) to decode the values for reference:
```
$ rtl_433 -f 433964000 -R 42
Registering protocol [1] "HIDEKI TS04 Temperature, Humidity, Wind and Rain Sensor"
Registered 1 out of 95 device decoding protocols
Found 1 device(s)

trying device  0:  Realtek, RTL2838UHIDIR, SN: 00000001
Found Rafael Micro R820T tuner
Using device 0: Generic RTL2832U OEM
Exact sample rate is: 250000.000414 Hz
[R82XX] PLL not locked!
Sample rate set to 250000.
Bit detection level set to 0 (Auto).
Tuner gain set to Auto.
Reading samples in async mode...
Tuned to 433964000 Hz.
2017-11-10 17:11:47 :	HIDEKI TS04 sensor
	Rolling Code:	 1
	Channel:	 1
	Battery:	 OK
	Temperature:	 22.1 C
	Humidity:	 41 %
2017-11-10 17:11:47 :	HIDEKI TS04 sensor
	Rolling Code:	 1
	Channel:	 1
	Battery:	 OK
	Temperature:	 22.1 C
	Humidity:	 41 %
2017-11-10 17:11:47 :	HIDEKI TS04 sensor
	Rolling Code:	 1
	Channel:	 1
	Battery:	 OK
	Temperature:	 22.1 C
	Humidity:	 41 %
```


# References
* https://github.com/pimatic/rfcontroljs/issues/68
* https://github.com/merbanan/rtl_433
* http://www.hidekielectronics.com/?m=99
