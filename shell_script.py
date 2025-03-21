from machine import Pin, I2C
import bmp280
import time


i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

def connect_sensor():
    """ Attempt to connect to the sensor """
    try:
        bmp = bmp280.BMP280(i2c=i2c)
        return bmp
        return True
    except Exception as e:
        print(f"Failed to connect to BMP280 sensor: {e}")
        return None
    
def sensor_reading():
    """ Reading sensor data """
    bmp = connect_sensor()
    temp = bmp.temperature
    pressure = bmp.pressure
    return temp, pressure

for _ in range(10):
    temp, pressure  = sensor_reading()
    print(f"Temperature: {temp} °C | Pressure: {pressure} hPa")
    time.sleep(1)