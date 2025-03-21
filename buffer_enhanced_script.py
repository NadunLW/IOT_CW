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
buffer_file = "data_buffer.txt"

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
        
def append_buffer(timestamp, temp, pressure):
    """ Append data to the buffer file. """
    try:
        with open(buffer_file, "a") as file:
            file.write(f"{timestamp}, {temp}, {pressure}\n")
        except Exception as e:
            print(f"Error writing to buffer: {e}")

def flush_buffer():
    """ Attempt to resend connected data during network absence. """
    try:
        with open(buffer_file, "r") as file:
            lines = file.readlines()
            
        successful_lines = []
        for line in lines:
            try:
                timestamp, temp, pressure = line.strip().split(",")
                sendToSpreadSheet(time=timestamp, temp=float(temp), pressure=float(pressure))
                successful_lines.append(line)
            except Exception as e:
                print(f"Failed to send buffered data: {e}")
                
        # Rewrite buffer file with unsent data
        with open(buffer_file, "w") as file:
            for line in lines:
                if line not in successful_lines:
                    file.write(line)
    except OSError:
        print("No buffer file found - nothing to flush.")

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
    """ Get current time using API """
    try:
        res=urequests.get(url=TIME_URL)
        time = json.loads(res.text)["dateTime"]
        res.close()
        return time
    except Exception as e:
        print(f"An error occured: {e}")
        return None

def sendToSpreadSheet(time, temp, pressure):
    """ Send data to Google Sheets """
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

    for _ in range(30): # Record 30 readings
        board_led.on()
        timestamp = f"{get_time()}"
        temp, pressure = sensor_reading()
        print(f"Temp: {temp} | Press: {pressure}")
        try:
            sendToSpreadSheet(time=timestamp, temp=temp, pressure=pressure)
        except Exception:
            print("Network error - saving to buffer....")
            append_buffer(timestamp, temp, pressure)
        
        flush_buffer()
        led_blink(3) # Feedback on data sent
        
    board_led.off()

main()

