from machine import Pin, I2C
import time
import bmp280
import network
import urequests
import json
import gc

# Hardware components 
board_led=machine.Pin("LED", machine.Pin.OUT)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Network variables
ssid = "Siphone"
password = "ygbpcccc"
wlan = network.WLAN(network.STA_IF)
SCRIPT_URL='https://script.google.com/macros/s/AKfycbwgNEP65YMJuzRyx4CX2I3Rhm3RoUYzziEkr5i2-Ha8aemu3X_qcMu4UZBsfInMrzpfvA/exec'
TIME_URL ='https://timeapi.io/api/time/current/zone?timeZone=Asia%2FColombo'

def led_blink(duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        board_led.on()
        time.sleep(0.2)
        board_led.off()
        time.sleep(0.2)

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
    """ Get temperature and pressure readings """
    bmp = connect_sensor()
    temp = bmp.temperature
    pressure = bmp.pressure
    return temp, pressure

def connect_wifi(ssid, password):
    """ Connect with specified network """
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    return ip
    
def get_time():
    try:
        res=urequests.get(url=TIME_URL)
        time = json.loads(res.text)["dateTime"]
        res.close()
        return time
    except Exception as e:
        print(f"An error occured: {e}")
        return None

def sendToSpreadSheet(time, temp, pressure):
    try:
        url=f"{SCRIPT_URL}?time={time}&temp={temp}&pressure={pressure}"
        print(url)
        res=urequests.get(url=url)
        print("Data sent...")
        res.close()
        gc.collect()
    
    except NameError:
        print("Error..."+NameError)
        return None

def main():
    connect_wifi(ssid, password)
    wlan.active(True)
    count = 0

    for _ in range(30):
        board_led.on()
        timestamp = f"{get_time()}"
        temp, pressure = sensor_reading()
        print(f"Temp: {temp} | Press: {pressure}")
        sendToSpreadSheet(time=timestamp, temp=temp, pressure=pressure)
        led_blink(3)
        
    board_led.off()

main()
