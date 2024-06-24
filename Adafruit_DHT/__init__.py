import random

DHT22 = 'DHT22'


def read_retry(sensor, pin):
    temperature = random.randrange(15, 43)
    humidity = random.randrange(30, 90)
    return temperature, humidity
