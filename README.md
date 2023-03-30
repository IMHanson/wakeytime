# Wakey-Time Nightlight
Esp32 based nightlight that updates to show whether it is bedtime (sleepy-time) or time to get up (wakey-time)

Inspired by the OK to Wake Light by Riley Parish https://github.com/rileyparish/ESP32OkToWakeLight 3d-files: https://www.thingiverse.com/thing:5573769

This light checks a Firebase-realtime database to get the default times for wakey-time (when it is ok to get up in the morning) and sleepy-time (bed-time).
The code then compares the local time (which it gets from an ntp server, factoring in DST and timezone) with these two times and updates the light accordingly.

I have replaced the nap-button with a 'Dance' button that makes the leds blink/flash in a short light-show.
You can connect to a webpage that is hosted on the esp32 to check/change the time settings, as well as engaging 'Slumber-mode' which delays the time set
to get up in the morning by a specified length of time (default: 30min). The site also includes a 'Dance' button that triggers the light-show.
