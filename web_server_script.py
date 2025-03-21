from machine import Pin, I2C
import bmp280
import time
import network
import socket

ssid = "Siphone"
password = "ygbpcccc"

# BMP280 connection
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

def connect_sensor():
    """ Attempt to connect to the sensor """
    try:
        bmp = bmp280.BMP280(i2c=i2c)
        return bmp
        
    except Exception as e:
        print(f"Failed to connect to BMP280 sensor: {e}")
        return None
    
def sensor_reading():
    """ Reading sensor data """
    bmp = connect_sensor()
    if bmp is None:
        return 0.0, 0.0
    
    temp = bmp.temperature
    pressure = bmp.pressure
    return temp, pressure

def connect_wifi(ssid, password):
    """ Connect with specified network """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Check available networks 
    print("Scanning available networks...")
    nets = wlan.scan()
    for net in nets:
        print(net[0].decode("utf-8"))
        
    max_attempts = 10
    for _ in range(max_attempts):
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print(f"Connected on {ip}")
            return ip
        print("Waiting for connection...)
        time.sleep(1)
    
    print("Connection failed.")
    return None

        
    
 
def open_socket(ip):
""" Open socket to establish connection """
    address = (ip, 80)
    connection = socket.socket()
    try:
        connection.bind(address)
        connection.listen(1)
        print(f"Listing on {ip}:80")
        return connection
    except OSError as e:
        print(f"Socket error: {e}")
        return None

def webpage(temp, pressure):
    # HTML face
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Pico W Weather Station</title>
            <meta http-equiv="refresh" content="5">
            </head>
            <body>
            <p>Temperature: {temp:.2f} C</p>
            <p>Atmospheric Pressure: {pressure:.2f} hPa</p>
            </body>
            </html>
            """
    return str(html)

def server(connection):
    """ Server to handle incoming requests """
    while True:
        try:
            client = connection.accept()
            request = str(client.recv(1024))
            
            temp, pressure = sensor_reading()
            html = webpage(temp, pressure)
            
            client.send('HTTP/1.1 200 OK\n')
            client.send('Content-Type: text/html\n')
            client.sendall(html)
            client.close()
        
        except Exception as e:
            print(f"Server error: {e}")

def main():
    
    ip = connect_wifi(ssid, password)
    if ip is None:
        print("failed to connect to network...")
        return 
    connection = open_socket(ip)
    server(connection)
    
main()
