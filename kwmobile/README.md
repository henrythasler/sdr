# kwmobile 433Mhz temperature and humidity sensor

## Prerequisites

- install [pigpiod](http://abyz.me.uk/rpi/pigpio/download.html)

## analyze samples

rtl_sdr -f 434000000 -s 2048000 sample.cu8

Analyze the data with inspectrum: `$ inspectrum sample.cu8`

## Decoding Rules

Symbol | Meaning | Comment
--- | --- | ---
`very short` pulse followed by `short` gap | `0` | 
`very short` pulse followed by `long` gap | `1` | 
`very short` pulse followed by `very long` gap | end of frame | 

Type | Timing
--- | --- 
`very short` | 500µs
`short` | 1000µs
`long` | 2000µs
`very long` | 4000µs

```
$ rtl_433 -vv- a -f 433.92M -s 1024k
time      : 2019-02-09 10:10:19
model     : Nexus Temperature/Humidity             House Code: 128
Channel   : 1            Battery   : OK            Temperature: 27.30 C      Humidity  : 96 %
pulse_demod_ppm(): Nexus Temperature & Humidity Sensor 
bitbuffer:: Number of rows: 12 
[00] {36} 80 81 11 f6 00 : 10000000 10000001 00010001 11110110 0000
[01] {36} 80 81 11 f6 00 : 10000000 10000001 00010001 11110110 0000
[02] {36} 80 81 11 f6 00 : 10000000 10000001 00010001 11110110 0000
[03] {36} 80 81 11 f6 00 : 10000000 10000001 00010001 11110110 0000

```

## References

- https://github.com/merbanan/rtl_433/blob/master/src/devices/nexus.c