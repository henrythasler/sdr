# kwmobile 433Mhz temperature and humidity sensor


rtl_sdr -f 434000000 -s 2048000 sample.cu8

Analyze the data with inspectrum: `$ inspectrum sample.cu8`


```
$ rtl_433 -f 433.92M -s 1024k
rtl_433 version 18.12-87-g19877ad branch master at 201902071346 inputs file rtl_tcp RTL-SDR
Trying conf file at "rtl_433.conf"...
Trying conf file at "/home/henry/.config/rtl_433/rtl_433.conf"...
Trying conf file at "/usr/local/etc/rtl_433/rtl_433.conf"...
Trying conf file at "/etc/rtl_433/rtl_433.conf"...
Registered 96 out of 120 device decoding protocols [ 1-4 8 11-12 15-17 19-21 23 25-26 29-36 38-60 62-64 67-71 73-100 102-103 108-116 119 ]
Detached kernel driver
Found Rafael Micro R820T tuner
[R82XX] PLL not locked!
Sample rate set to 1024000 S/s.
Tuner gain set to Auto.
Tuned to 433.920MHz.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
time      : 2019-02-07 21:09:11
model     : Nexus Temperature/Humidity             House Code: 128
Channel   : 1            Battery   : OK            Temperature: 20.60 C
Humidity  : 61 %
```