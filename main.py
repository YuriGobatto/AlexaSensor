import datetime
import http.client as httplib
import json
import sys
import time
from pathlib import Path

import Adafruit_DHT


def log(message):
    print(prefix_datetime(message))


def prefix_datetime(message):
    iso_now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return "[%s] %s" % (iso_now, message)


def have_internet():
    conn = httplib.HTTPConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()


measurement = 'rpi-dht22'
location = 'bedroom'

sensor = Adafruit_DHT.DHT22
sensor_gpio = 4

humidity, temperature = Adafruit_DHT.read_retry(sensor, sensor_gpio)
if humidity is None and temperature is None:
    sys.exit(prefix_datetime(
        "There was an error fetching the temperature data. (Humidity: %s, Temperature: %s)" % (humidity, temperature)))

humidity = round(humidity, 2)
temperature = round(temperature, 2)
iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
log("Temp: %s, Humidity: %s" % (temperature, humidity))

data = [
    {
        "measurement": measurement,
        "tags": {
            "location": location,
        },
        "time": iso,
        "fields": {
            "temperature": temperature,
            "humidity": humidity
        }
    }
]
f = open(Path('bedroom-temperature-api', 'temperature.json'), 'w')
f.write(json.dumps(data[0], sort_keys=True, indent=4))
f.close()
log("Commit")

push_command_result = 0
for i in range(3):
    push_command_result = 0
    if push_command_result == 0:
        sys.exit(0)
    sleep = 3 ** i * 3
    log("Failed to push to GitHub, sleeping for %s" % sleep)
    time.sleep(sleep)

if not have_internet():
    log("Internet is down")
    sys.exit(1)
else:
    log("Internet is available")

log("Git repo probably corrupt, re-cloning")
