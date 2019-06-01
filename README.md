# raspberry-thermostat
Project to transform your Raspberry Pi into a thermosat


## Initial steps


To make the script work, a few initial steps are required:

1. Enable 1-Wire interface on your raspberry:

  run ```sudo raspi-config```
  select "Interface options"
  select "1-Wire"
  choose "Yes" when promtped if you like the 1-Wire interface to be enabled
2. Wire the sensor:
  power cable to PIN 1 (3.3V)
  ground cable to PIN 6
  sensor cable to PIN 7 (GPIO4)


## TODOs

The initial version of the script uses the GPIO4 pin. Change it to accept the pin number as an input parameter with the default value set to 4.
The script is executing the `modprobe w1-gpio` and `modprobe w1-therm` commands at the beginning, but it could be better to add them in the /etc/modules file so they're loaded on Raspberry's startup
