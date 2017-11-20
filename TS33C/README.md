# Hideki TS33C Wireless Temperature/Humidity Sensor
Analysis and decoding of temperatures and humidity values sent by this wireless sensor.

# Technical Specifications

Item | Value | Description
-------------: | ------------- | :-------------
Frequency  | 433.964MHz |

# Decoding Tool
Analyze the radio data with:
```
$ rtl_433 -f 433964000 -R 42 -DD
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
Pulse data: 1 pulses
[  0] Pulse:   15, Gap: 2501, Period: 2516
2017-11-19 20:22:35 :	HIDEKI TS04 sensor
	Rolling Code:	 1
	Channel:	 1
	Battery:	 OK
	Temperature:	 20.7 C
	Humidity:	 48 %
pulse_demod_clock_bits(): HIDEKI TS04 Temperature, Humidity, Wind and Rain Sensor
bitbuffer:: Number of rows: 1
[00] {90} 06 bd e3 d0 c1 f5 e3 b6 01 3c f8 40
Pulse data: 68 pulses
[  0] Pulse:  239, Gap:  259, Period:  498
[  1] Pulse:  229, Gap:  258, Period:  487
[  2] Pulse:  230, Gap:  138, Period:  368
[  3] Pulse:  106, Gap:  137, Period:  243
[  4] Pulse:  107, Gap:  261, Period:  368
[  5] Pulse:  107, Gap:  138, Period:  245
[  6] Pulse:  227, Gap:  138, Period:  365
[  7] Pulse:  106, Gap:  139, Period:  245
[  8] Pulse:  106, Gap:  137, Period:  243
[  9] Pulse:  107, Gap:  136, Period:  243
[ 10] Pulse:  108, Gap:  260, Period:  368
[ 11] Pulse:  105, Gap:  138, Period:  243
[ 12] Pulse:  106, Gap:  138, Period:  244
[ 13] Pulse:  106, Gap:  140, Period:  246
[ 14] Pulse:  106, Gap:  136, Period:  242
[ 15] Pulse:  229, Gap:  260, Period:  489
[ 16] Pulse:  228, Gap:  142, Period:  370
[ 17] Pulse:  103, Gap:  139, Period:  242
[ 18] Pulse:  105, Gap:  136, Period:  241
[ 19] Pulse:  107, Gap:  140, Period:  247
[ 20] Pulse:  106, Gap:  261, Period:  367
[ 21] Pulse:  105, Gap:  140, Period:  245
[ 22] Pulse:  226, Gap:  260, Period:  486
[ 23] Pulse:  229, Gap:  259, Period:  488
[ 24] Pulse:  106, Gap:  137, Period:  243
[ 25] Pulse:  107, Gap:  139, Period:  246
[ 26] Pulse:  227, Gap:  261, Period:  488
[ 27] Pulse:  228, Gap:  261, Period:  489
[ 28] Pulse:  227, Gap:  144, Period:  371
[ 29] Pulse:   99, Gap:  140, Period:  239
[ 30] Pulse:  105, Gap:  138, Period:  243
[ 31] Pulse:  108, Gap:  136, Period:  244
[ 32] Pulse:  108, Gap:  137, Period:  245
[ 33] Pulse:  108, Gap:  257, Period:  365
[ 34] Pulse:  106, Gap:  140, Period:  246
[ 35] Pulse:  229, Gap:  138, Period:  367
[ 36] Pulse:  106, Gap:  139, Period:  245
[ 37] Pulse:  103, Gap:  139, Period:  242
[ 38] Pulse:  105, Gap:  143, Period:  248
[ 39] Pulse:  102, Gap:  260, Period:  362
[ 40] Pulse:  228, Gap:  264, Period:  492
[ 41] Pulse:  104, Gap:  137, Period:  241
[ 42] Pulse:  107, Gap:  136, Period:  243
[ 43] Pulse:  107, Gap:  138, Period:  245
[ 44] Pulse:  229, Gap:  139, Period:  368
[ 45] Pulse:  105, Gap:  138, Period:  243
[ 46] Pulse:  106, Gap:  260, Period:  366
[ 47] Pulse:  105, Gap:  138, Period:  243
[ 48] Pulse:  106, Gap:  138, Period:  244
[ 49] Pulse:  230, Gap:  263, Period:  493
[ 50] Pulse:  224, Gap:  259, Period:  483
[ 51] Pulse:  230, Gap:  258, Period:  488
[ 52] Pulse:  230, Gap:  259, Period:  489
[ 53] Pulse:  107, Gap:  140, Period:  247
[ 54] Pulse:  227, Gap:  260, Period:  487
[ 55] Pulse:  106, Gap:  138, Period:  244
[ 56] Pulse:  105, Gap:  139, Period:  244
[ 57] Pulse:  106, Gap:  138, Period:  244
[ 58] Pulse:  106, Gap:  138, Period:  244
[ 59] Pulse:  229, Gap:  260, Period:  489
[ 60] Pulse:  106, Gap:  141, Period:  247
[ 61] Pulse:  103, Gap:  136, Period:  239
[ 62] Pulse:  109, Gap:  136, Period:  245
[ 63] Pulse:  108, Gap:  137, Period:  245
[ 64] Pulse:  107, Gap:  137, Period:  244
[ 65] Pulse:  229, Gap:  261, Period:  490
[ 66] Pulse:  227, Gap:  268, Period:  495
[ 67] Pulse:   97, Gap: 2501, Period: 2598
```
or

```
$ rtl_433 -f 433964000 -A
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
Detected OOK package	@ 2017-11-19 13:46:15
2017-11-19 13:46:15 :	HIDEKI TS04 sensor
	Rolling Code:	 1
	Channel:	 1
	Battery:	 OK
	Temperature:	 22.1 C
	Humidity:	 43 %
Analyzing pulses...
Total count:   69,  width: 22000		(88.0 ms)
Pulse width distribution:
 [ 0] count:   22,  width:   234 [230;247]	( 936 us)
 [ 1] count:   46,  width:   111 [106;114]	( 444 us)
 [ 2] count:    1,  width:    16 [16;16]	(  64 us)
Gap width distribution:
 [ 0] count:   22,  width:   254 [252;259]	(1016 us)
 [ 1] count:   46,  width:   132 [130;139]	( 528 us)
Pulse period distribution:
 [ 0] count:   13,  width:   489 [484;500]	(1956 us)
 [ 1] count:   18,  width:   366 [361;370]	(1464 us)
 [ 2] count:   37,  width:   243 [239;248]	( 972 us)
Level estimates [high, low]:  15581,     19
Frequency offsets [F1, F2]:     473,      0	(+1.8 kHz, +0.0 kHz)
Guessing modulation: Pulse Width Modulation with startbit/delimiter
Attempting demodulation... short_limit: 63, long_limit: 172, reset_limit: 260, demod_arg: 0
pulse_demod_pwm_ternary(): Analyzer Device
bitbuffer:: Number of rows: 2
[00] {68} e2 01 83 50 08 61 79 83 00
[01] {0} :
```


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

## decoding sequence rtl_433
1. rtlsdr_callback()
2. Convert to magnitude and filter
3. pulse_detect_package()
4. pulse_demod_clock_bits()
5. hideki_ts04_callback()




# References
* https://github.com/pimatic/rfcontroljs/issues/68
* https://github.com/merbanan/rtl_433
* http://www.hidekielectronics.com/?m=99
* https://github.com/kevinmehall/rtlsdr-433m-sensor
