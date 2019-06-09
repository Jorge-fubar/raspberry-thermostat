# raspberry-thermostat
Project to transform your Raspberry Pi into a thermosat


## Initial steps


To make the script work, a few initial steps are required:

1. Enable 1-Wire interface on your raspberry:
  - run `sudo raspi-config`
  - select "Interface options"
  - select "1-Wire"
  - choose "Yes" when promtped if you like the 1-Wire interface to be enabled
2. Wire the sensor:
  - power cable to PIN 1 (3.3V)
  - ground cable to PIN 6
  - sensor cable to PIN 7 (GPIO4)
3. Make the screen turn off after X seconds
  By default Raspbian (version 9) sets the screen to idle after a fixed period of time not configurable by GUI (at least I've found or read about). To do so we need to add some config in a couple of system files:
  - run `sudo vim /boot/config.txt`
  - add the line `hdmi_blanking=1` to the file. This will prevent the screen blanking, turning the monitor off instead
  - run `sudo vim /etc/xdg/lxsession/LXDE-pi/autostart`
  - add the line `@xset dpms 0 0 X` to the file, where X is a number that specifies the amount of seconds the system will wait till it turns off the screen. For example, I've added to my file the line `@xset dpms 0 0 10`

## TODOs

The initial version of the script uses the GPIO4 pin. Change it to accept the pin number as an input parameter with the default value set to 4.
The script is executing the `modprobe w1-gpio` and `modprobe w1-therm` commands at the beginning, but it could be better to add them in the /etc/modules file so they're loaded on Raspberry's startup
