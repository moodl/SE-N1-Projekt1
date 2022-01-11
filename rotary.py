""" Team1 Nördlingen:
rotary.py steuert den Rotary_Encoder

Wichtige Funktionen für nachfolgende Programme:
    -init_port(callback)    Initialisiert alle Ports als Eingänge die mit den Rotary-Encoder verbunden sind.
                            Die Übergebene Funktion wird beim Interrupt aufgerufen.

    -ein()                  Aktiviert den Interrupt.

    -aus()                  Deaktiviert den Interrupt.
"""
import RPi.GPIO as GPIO

#Pins als Variablen festlegen
CLOCKPIN = 14           #Pin der mit CLK vom Rotary Encoder verbunden ist
DATAPIN = 15            #Pin der mit DT vom Rotary Encoder verbunden ist
DEBOUNCE = 350          #Debounce time in ms bis Interupt vom Rotary Encoder erneut auslösen kann


def init_port(mycallback):  
    """Initialisiert alle Ports als Eingänge die mit dem Rotary-Encoder verbuden sind.
       Definiert die callback Funktion die beim Interrupt ausgelöst wird.

    Args: 
        Callback Funktion die beim Interrupt ausgelöst werden soll
    Return: 
        None
    """ 
    global my_callback
    GPIO.setmode(GPIO.BCM)                                      #Zahlen bedeuten die Nummern vom GPIO Channel
    GPIO.setwarnings(False)                                     #Schaltet Warnung aus
    GPIO.setup(CLOCKPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)     #Initialisiert die GPIOs als Eingänge mit pull_up
    GPIO.setup(DATAPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
    my_callback = mycallback                                    #Definiert die Callback Funktion die beim Interrupt ausgelöst werden soll


def ein():  
    """Aktiviert den Interrupt.

    Args:
        None
    Return:
        None
    """
    global my_callback           
    GPIO.add_event_detect(CLOCKPIN, GPIO.FALLING, callback=my_callback, bouncetime=DEBOUNCE)


def aus():
    """Deaktiviert den Interrupt.

    Args:
        None
    Return:
        None
    """              
    GPIO.remove_event_detect(CLOCKPIN)


#Debug Code
if __name__ == "__main__":
    s =0

    def callback(channel):
        global s
        data = GPIO.input(DATAPIN)
        if data == 1:
            s-=1
        else:
            s+=1

    init_port(callback)
    ein()
    time.sleep(60)
    aus()