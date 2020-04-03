import RPi.GPIO as GPIO
from time import sleep
import datetime
from firebase import firebase
import Adafruit_DHT
from os import popen as pop
import time

#libries setup for oled display and spi serial interface
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont

#Fonts and Size Setup For OLED Display
font = ImageFont.load_default()
font10 = ImageFont.truetype('Minecraftia.ttf',10)
font18 = ImageFont.truetype('Minecraftia.ttf',18)

#Initiated Display
padding = -2
top = padding
x = 3 #Dot Start Point
RST = 25
DC = 24
serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC, gpio_RST = RST)
device = sh1106(serial, rotate=2) #sh1106  

#Sensor Setup
sensor = Adafruit_DHT.DHT11
pin = 4
light_pin = 21
#Firebase Setup
firebase = firebase.FirebaseApplication('https://laxz-fired-project.firebaseio.com/', None)

# LOGGER to control program flow later as boolean
LOGGER = 1
def printlog(text):
    if(LOGGER):
        print(text)

# Start script
printlog("Script Started") #test

def readDHT22():
    # Initiate and Get data (Once) from Sensor
    humidity, temperature = Adafruit_DHT.read(sensor,pin)
    if humidity is not None and temperature is not None:
        temperature = ' {0:0.2f} \'C'.format(temperature)  
        humidity  = ' {0:0.2f} %'.format(humidity)
        return(temperature,humidity)
    else:
        return('Error','Error')

# Return CPU temperature as a character string                                      
def getCPUtemperature():
    res = pop('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

def getRAMinfo():
    p = pop('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

def getCPUuse():
    return(str(pop("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

def getDiskSpace():
    p = pop("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

def displayOLED():
    CPU_temp  = getCPUtemperature()
    CPU_usage = getCPUuse()
    temperature,humidity = readDHT22()
    printlog("Room Temperature: " +temperature)
    printlog("Room Humidity: "+humidity)
    with canvas(device) as make:
        make.rectangle(device.bounding_box, outline="white", fill="black")
        make.text((x,top+3),     "Welcome Sir,Min Latt",  font=font, fill=255)
        make.text((x,top+50), "Updated to Firebase" , font=font, fill=255)
        make.text((x, top+21),    "Temperature/Humidity",  font=font, fill=255)
        make.text((x, top+12),    "Load:" +str(CPU_usage) +" & Temp:"+ str(CPU_temp), font=font, fill=255)
        make.text((x, top+39), temperature, font=font10, fill=255)
        make.text((x+75, top+39), humidity, font=font10, fill=255)
##Date and time format
dateString = '%d/%m/%Y %H:%M:%S'

def updatePiInfo():
    printlog("======================================================")
    displayOLED()
    printlog("##Updating Raspberry Pi Info to Google Firebase..##")
    firebase.put("/Settings", "/last_update_datetime", datetime.datetime.now().strftime(dateString))

    temperature, humidity = readDHT22()
    firebase.put("/Controls/Sensors", "/Humidity/current_inside", ""+humidity) #+"%"
    firebase.put("/Controls/Sensors", "/Temperature/current_inside", ""+temperature) #+"C"

    #CPU INFO
    CPU_temp  = getCPUtemperature()
    CPU_usage = getCPUuse()
    firebase.put("/PI/CPU", "/temperature", CPU_temp)
    printlog("CPU Temp "+CPU_temp)

    #RAM INFO
    RAM_stats = getRAMinfo()
    RAM_total = round(int(RAM_stats[0]) / 1000,1)
    RAM_used = round(int(RAM_stats[1]) / 1000,1)
    RAM_free = round(int(RAM_stats[2]) / 1000,1)
    firebase.put("/PI/RAM", "/free", str(RAM_free)+"")
    firebase.put("/PI/RAM", "/used", str(RAM_used)+"")
    firebase.put("/PI/RAM", "/total", str(RAM_total)+"")    

    #DISK INFO
    DISK_stats = getDiskSpace()
    DISK_total = DISK_stats[0]
    DISK_free  = DISK_stats[1]
    DISK_perc  = DISK_stats[3]
    DISK_used  = float(DISK_total[:-1]) - float(DISK_free[:-1])
    firebase.put("/PI/DISK", "/total", str(DISK_total[:-1]))
    firebase.put("/PI/DISK", "/free", str(DISK_free[:-1]))
    firebase.put("/PI/DISK", "/used", str(DISK_used))
    firebase.put("/PI/DISK", "/percentage", str(DISK_perc))

    printlog(datetime.datetime.now().strftime(dateString))
    #printlog("Humidity: Current["+humidity+"], Max["+maxHumidity+"], Min["+minHumidity+"]")
    #printlog("Temperature: Current["+temperature+"], Max["+maxTemperature+"], Min["+minTemperature+"]")
    printlog("CPU temperature: "+CPU_temp)
    printlog("RAM total["+str(RAM_total)+" MB], RAM used["+str(RAM_used)+" MB], RAM free["+str(RAM_free)+" MB]")
    printlog("DISK total["+str(DISK_total)+"], free["+str(DISK_free)+"], perc["+str(DISK_perc)+"]")
    printlog("##Update finished successfully##")
    printlog("======================================================\n")

def min_max_sensor():
    maxHumidity = firebase.get("/Controls/Sensors/Humidity/max_inside", None)
    maxHumidity = maxHumidity[:-1]

    minHumidity = firebase.get("/Controls/Sensors/Humidity/min_inside", None)
    minHumidity = minHumidity[:-1]

    maxTemperature = firebase.get("/Controls/Sensors/Temperature/max_inside", None)
    maxTemperature = maxTemperature[:-1]

    minTemperature = firebase.get("/Controls/Sensors/Temperature/min_inside", None)
    minTemperature = minTemperature[:-1]

    if float(humidity) > float(maxHumidity):
        firebase.put("/Controls/Sensors", "/Humidity/max_inside", ""+humidity)
        printlog("Updated Humidity max_inside")
    if float(temperature) > float(maxTemperature):
        firebase.put("/Controls/Sensors", "/Temperature/max_inside", ""+temperature)
        printlog("Updated Temperature max_inside")

    if float(humidity) < float(minHumidity):
        firebase.put("/Controls/Sensors", "/Humidity/min_inside", ""+humidity)
        printlog("Updated Humidity min_inside")
    if float(temperature) < float(minTemperature):
        firebase.put("/Controls/Sensors", "/Temperature/min_inside", ""+temperature)
        printlog("Updated Temperature min_inside")

def light_up():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.output(light_pin,1)
def light_down():
    GPIO.output(light_pin,0)

try:
    while True:
        light_up()
        updatePiInfo()
        light_down()
        print("")
        #min_max_sensor()
        #Retrieve sleep time from firebase and continue the loop
        #sleepTime = firebase.get("/Settings/info_update_time_interval", None)
        #sleepTime = int(sleepTime)
        #sleep(sleepTime)
        time.sleep(5)
except KeyboardInterrupt:
        print("Interrupted")
        #continue



