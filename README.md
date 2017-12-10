# Intro
Collection of software defined radio (SDR) stuff

# Projects
* [FM-Radio](./FM-Radio)
* [Live Decoding of Hideki TS33C Wireless Temperature Sensor](./TS33C)
* [Live Decoding of TFA 30.3180.IT Wireless Temperature Sensor](./TFA)

# Hardware
I use a RTL2832U-based USB-receiver [RTL_SDR by Radioddity](https://www.radioddity.com/radioddity-100khz-1766mhz-0-1mhz-1-7ghz-full-band-uhf-vhf-hf-rtl-sdr-usb-tuner-receiver.html). It is shipped with a monopole antenna which works o.k. for most beginner use-cases (e.g. FM-Radio, 433MHz)

See https://www.rtl-sdr.com/ for more info.

# Software
* [CubicSDR](http://cubicsdr.com/)
* [baudline](http://baudline.com/index.html)

# Know-How
* [I/Q Data for Dummies](http://whiteboard.ping.se/SDR/IQ)


# How to git
1. git clone https://github.com/henrythasler/sdr.git
2. cd sdr
3. git remote add sdr https://github.com/henrythasler/sdr
4. // do something
5. git add .
6. git commit -a
7. git push sdr master
