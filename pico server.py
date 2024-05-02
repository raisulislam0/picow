import network
import socket
import time

from machine import Pin

led = machine.Pin("LED", machine.Pin.OUT)  # Assuming LED is connected to GPIO Pin 2

ssid = 'Wifi_Zone'
password = 'xxxxxx'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
<html>
    <head>
        <title>Pico W</title>
        <script>
            function toggleLED() {
                var xhr = new XMLHttpRequest();
                xhr.open("GET", "/toggle", true);
                xhr.send();
                if (document.getElementById("ledButton").innerHTML === "OFF") {
                    document.getElementById("ledButton").innerHTML = "ON";
                } else {
                    document.getElementById("ledButton").innerHTML = "OFF";
                }
            }
        </script>
    </head>
    <body>
        <h1>Pico W</h1>
        <button id="ledButton" type="submit" onclick="toggleLED()">OFF</button>
        <p>%s</p>
    </body>
</html>
"""

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print(request)

        request = str(request)
        led_toggle = request.find('/toggle')
        print('led toggle = ' + str(led_toggle))

        if led_toggle == 6:
            print("toggle led")
            led.value(not led.value())

        response = html % ("LED is ON" if led.value() else "LED is OFF")

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')

