import sqlite3
import RPi.GPIO as GPIO
import time

POWER_CONST=(1000*60*60)/96.0 #ws/U

GPIO_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


conn = sqlite3.connect("/home/pi/Desktop/energy/Data/power-data.db")
c = conn.cursor()
c.execute('DELETE from Power')
conn.commit()
conn.close()


print "database cleared"

