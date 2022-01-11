""" Team1 Nördlingen:
relais.py steuert das Relais

Wichtige Funktionen für nachfolgende Programme:
    -init_port()            Initialisiert alle Ports als Ausgänge die mit dem Relais verbunden sind.

    -motor_ein()            Schaltet die Ausgänge so, dass der Motor einfährt.

    -motor_aus()            Schaltet die Ausgänge so, dass der Motor ausfährt.

    -motor_stop()           Schaltet die Ausgänge so, dass der Motor anhält.

    -magnet_ein()           Schaltet die Ausgänge so, dass der Magnet an ist.

    -magnet_aus()           Schaltet die Ausgänge so, dass der Magnet aus ist.
"""

import RPi.GPIO as GPIO

#Pins als Variable festlegen
Motor_schwarz = 26          #Pin führt zu Relais das Motor_schwarz-Kabel steuert
Motor_rot     = 19          #Pin führt zu Relais das Motor_rot-Kabel steuert
Magnet        = 13          #Pin führt zu Relais das Magnet steuert


def init_port():      
    """Initialisiert alle Ports als Ausgänge die mit dem Relais verbuden sind.

    Args: 
        None
    Return: 
        None
    """ 
    GPIO.setmode(GPIO.BCM)                  #Zahlen bedeuten die Nummern vom GPIO Channel
    GPIO.setwarnings(False)                 #Schaltet Warnung aus
    GPIO.setup(Motor_rot    , GPIO.OUT)     #Initialisiert die GPIOs als Ausgänge
    GPIO.setup(Motor_schwarz, GPIO.OUT)
    GPIO.setup(Magnet       , GPIO.OUT)

def motor_ein():                 
    """Schaltet die Ausgänge so, dass der Motor einfährt.

    Args:
        None
    Return:
        None
    """
    GPIO.output(Motor_rot,GPIO.HIGH)        #Schaltet die Ausgänge auf High bzw. Low
    GPIO.output(Motor_schwarz,GPIO.LOW)

def motor_aus():                              
    """Schaltet die Ausgänge so, dass der Motor ausfährt.

    Args:
        None
    Return:
        None
    """
    GPIO.output(Motor_rot,GPIO.LOW)         #Schaltet die Ausgänge auf High bzw. Low
    GPIO.output(Motor_schwarz,GPIO.HIGH)      

def motor_stop():                             
    """Schaltet die Ausgänge so, dass der Motor anhält.

    Args:
        None
    Return:
        None
    """
    GPIO.output(Motor_rot,GPIO.LOW)         #Schaltet die Ausgänge auf Low
    GPIO.output(Motor_schwarz,GPIO.LOW)          

def magnet_ein():
    """Schaltet die Ausgänge so, dass der Magnet an ist.

    Args:
        None
    Return:
        None
    """                            
    GPIO.output(Magnet,GPIO.LOW)            #Schaltet den Ausgang auf Low
    
def magnet_aus():                           
    """Schaltet die Ausgänge so, dass der Magnet aus ist.

    Args:
        None
    Return:
        None
    """
    GPIO.output(Magnet,GPIO.HIGH)           #Schaltet den Ausgang auf High



#Debug Code
if __name__ == "__main__":
    init_port()
    magnet_ein()
    time.sleep(5)
    magnet_aus()
    GPIO.cleanup()
