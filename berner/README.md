# berner remote control


# Technical Specifications
Item | Value | Description
-------------: | ------------- | :-------------
Model | BHS140
Radio | fixed code, unidirectional
Channels | 4 |
Frequency  | 868.2MHz |
Symbol-Rate | 1 kHz |
Coding | ? |

## analyze samples

```
$ rtl_sdr -f 868000000 -s 2048000 sample.cu8
Found 1 device(s):
  0:  Realtek, RTL2838UHIDIR, SN: 00000001

Using device 0: Generic RTL2832U OEM
Found Rafael Micro R820T tuner
[R82XX] PLL not locked!
Sampling at 2048000 S/s.
Tuned to 868000000 Hz.
Tuner gain set to automatic.
Reading samples in async mode...
^CSignal caught, exiting!

User cancel, exiting...

$ inspectrum sample.cu8 
```

# Decoding Tool


# References
* http://berner-torantriebe.eu/files/berner_handsender_090516.pdf
