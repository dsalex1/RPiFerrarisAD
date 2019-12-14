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


print "RPi ferraris measurer [Press STRG+C, to exit the Test]"


timeLast=None

def outputFunction(arg):
    global timeLast
	
    if (timeLast!=None and time.time()-timeLast>0):
        print ("output seconds: "+str(time.time()-timeLast))	
        timePassed=time.time()-timeLast
	
        conn = sqlite3.connect("/home/pi/Desktop/energy/Data/power-data.db")
        c = conn.cursor()

        c.execute('insert into Power values (?,?)', [int(time.time()-timePassed/2),POWER_CONST/timePassed])
        conn.commit()
        conn.close()
		
    timeLast=time.time()

	
GPIO.add_event_detect(GPIO_PIN, GPIO.RISING, callback=outputFunction, bouncetime=1000) 




try:
	while True:
		time.sleep(10)
except KeyboardInterrupt:
    GPIO.cleanup()
