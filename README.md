# SDR-Intro

Collection of software defined radio (SDR) stuff

## Projects

* [FM-Radio](./FM-Radio)
* [Live Decoding of Hideki TS33C Wireless Temperature Sensor](./TS33C)
* [Live Decoding of TFA 30.3180.IT Wireless Temperature Sensor](./TFA)
* [Berner garage door opener remote control](./berner)
* [somfy sunshade remote control](./somfy)
* [mumbi remote controlled power outlets](./mumbi)

## Getting Started

1. plug in the USB-Receiver
2. Install drivers as described in [Quick Start Guide](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)
## Hardware

I use a RTL2832U-based USB-receiver [RTL_SDR by Radioddity](https://www.radioddity.com/radioddity-100khz-1766mhz-0-1mhz-1-7ghz-full-band-uhf-vhf-hf-rtl-sdr-usb-tuner-receiver.html). It is shipped with a monopole antenna which works o.k. for most use-cases (e.g. FM-Radio, 433MHz, 868MHz). To increase the mobility of the whole setup you might want to exchange the stock antenna for a [smaller version](https://de.aliexpress.com/item/GSM-868M-900M-915MHz-antenna-2dbi-SMA-male-connector-5cm-long-RC-Receive-transmit-aerial-2/32511895558.html).

If you want to spend more money you might go for a [HackRF One](https://greatscottgadgets.com/hackrf/)

## Software (Linux)

* [SDR++](https://github.com/AlexandreRouma/SDRPlusPlus)
* [inspectrum](https://github.com/miek/inspectrum)
* [baudline](http://baudline.com/index.html)

## References

* [I/Q Data for Dummies](http://whiteboard.ping.se/SDR/IQ)
* [RTL-SDR (RTL2832U) and software defined radio news and projects](https://www.rtl-sdr.com/)
