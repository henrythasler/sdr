# Somfy Telis 1 RTS remote control

Remote control for various home appliances.

## Technical Specifications

Item | Value | Description
-------------: | ------------- | :-------------
Frequency  | 433.42 MHz |
Symbol-rate | 775 Bd
Encoding | Manchester | rising edge = 1, falling edge = 0

## Signal Charactersistics

Frame including leading Wake-up pulse:
![Frame including WUP](docs/spectrum_magnitude.png)

Sync pattern and start of frame:
![Start of frame](docs/start_of_frame.png)

Decoding of frame data according to [Somfy Smoove Origin RTS Protocol](https://pushstack.wordpress.com/somfy-rts-protocol/)

## Decoding Tool

`sniff.py` - a command-line tool to read and decode hand-held transmitter data using my [python RFM69-library](https://github.com/henrythasler/rfm69)

```bash
$ python sniff.py
Scanning... Press Ctrl-C to abort
Clock Sync: [ 2520.  2625.  2495.  2615.] 640
Frame: 0xA6 0x16 0x11 0x46 0xBD 0x5F 0x36
    Control: 0x01
    Checksum: ok
    Address: BD 5F 36
    Rolling Code: 11 46
```

The RFM69 Data-Pin looks like this:
![Start of frame](docs/data_pin.png)

## Transmission

To set up your own transmitter, follow the pairing-process as follows:

1. optional: create and adapt `config.json` to set a custom address for the new transmitter
2. long-press the PROG-button on a paired remote until the device (e.g. a shade) jogs
3. transmit the `prog` command with `transmitter.py`. The device will jog again indicating that a new transmitter is paired
4. send regular commands

```bash
$ sudo python3 transmitter.py down
key: 0xA0, ctrl: 0x04, rolling code: 0x03, address: 0x365240
cksum: 8
Data: 0xA3 0x48 0x00 0x03 0x40 0x52 0x36 
Frame: 0xA3 0xEB 0xEB 0xE8 0xA8 0xFA 0xCC
```

The rolling code is automatically incremented and saved to `config.json`.

## References

* https://www.somfy.de/produkte/1810630/telis-1-rts-
* [Somfy Smoove Origin RTS Protocol](https://pushstack.wordpress.com/somfy-rts-protocol/)
* [NodeMCU Somfy module](https://nodemcu.readthedocs.io/en/master/en/modules/somfy/)
* [Quick Programming Guide for all Somfy® RTS Motors](https://www.thejustdesigngroup.net/automatedshade/documents/RTS%20Quick%20Programming%20Guide.pdf)

