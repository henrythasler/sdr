# TFA Dostmann Thermo-Hygro Sensor 30.3180.IT


# Technical Specifications
Item | Value | Description
-------------: | ------------- | :-------------
Model | 30.3180.IT
Radio | ??
Frequency  | 868.25MHz |
Bit-timing | ? |
Baudrate | 38400 |
Coding | RZ |

# Decoding Tool
Use https://github.com/baycom/tfrec as reference for decoding:

```
$ ./tfrec -D -S ~/sdr/sdr/TFA/sample.raw | grep 71c9
Found Rafael Micro R820T tuner
#000 1512819632  2d d4 71 c9 86 14 36 60 00 56 5e           ID 71c9 +21.4 54%  seq 0 lowbat 0 RSSI 81
```

0x71, 0xc9, 0x86, 0x14, 0x36, 0x60, 0x00, 0x56


# References
* https://nccgroup.github.io/RFTM/fsk_receiver.html
* https://www.reaktor.com/blog/radio-waves-packets-software-defined-radio/
* http://tfa-dostmann.de/index.php?id=129&L=0
* https://github.com/sum-sum/rtl_868
* http://www.linux-magazine.com/Online/Features/Reading-Weather-Data-with-Software-Defined-Radio
* https://github.com/ChristopheJacquet/Pydemod
* http://www.sunshine2k.de/coding/javascript/crc/crc_js.html




