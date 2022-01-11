""" Team1 Nördlingen:
zeit.py steuert die Zeitmessung

Wichtige Funktionen für nachfolgende Programme:
    -init_port()            Initialisiert alle Ports als Eingänge die mit den Lichtschranken verbunden sind.

    -wait_for_1()           Wartet so lange bis die Erste Lichtschranke unterbrochen wird.

    -wait_for_taster()      Wartet so lange bis der Taster gedrückt wird.

    -mess_zeit(ausgabe)     Führt die Zeitmessung aus.
                            Übergabewert !=None führt zur Ausgabe der Messwerte in der Konsole.
"""
import RPi.GPIO as GPIO
import time

import relais       #Zur steuerung vom Magnet

#Pins als Variable festlegen
GPIO_taster = 4     #Pin Taster
GPIO_L1     = 10    #Pin Lichtschranke 1
GPIO_L2     = 9     #Pin Lichtschranke 2 
GPIO_L3     = 11    #Pin Lichtschranke 3 (Ziel)
time_tuple = ()     #Tuple wo die Zeiten gespeichert werden


def init_port():
    """Initialisiert alle Ports als Eingänge die mit den Lichtschranken verbun sind.

    Args: 
        None
    Return: 
        None
    """                   
    GPIO.setmode(GPIO.BCM)                  #Zahlen bedeuten die Nummern vom GPIO Channel
    GPIO.setwarnings(False)                 #Schaltet Warnung aus
    GPIO.setup(GPIO_L1,     GPIO.IN)        #Initialisiert die GPIOs als Eingänge
    GPIO.setup(GPIO_L2,     GPIO.IN)          
    GPIO.setup(GPIO_L3,     GPIO.IN)             
    GPIO.setup(GPIO_taster, GPIO.IN)
   

def wait_for_1():
    """Wartet so lange bis die Erste Lichtschranke unterbrochen wird.

    Args: 
        None
    Return: 
        None
    """        
    GPIO.wait_for_edge(GPIO_L1, GPIO.RISING)
   
def wait_for_taster():
    """Wartet so lange bis der Taster gedrückt wird.

    Args: 
        None
    Return: 
        None
    """    
    GPIO.wait_for_edge(GPIO_taster, GPIO.FALLING)

def mess_zeit(ausgabe = None):          
    """Führt die Zeitmessung aus.

    Die 50ms sleeps zwischen den GPIO wait vor Edge entstanden, da beim Testen nach mehreren Malen die
    Edge erkennung nicht mehr richtig funktionierte. Ist soweit kein Problem, außer die Zeit zwischen
    den Messpunkten sinkt unter 50ms.

    Args: 
        ausgabe: Wenn irgendwas übergeben wird außer None, folgt eine Ausgabe der Messwerte

    Return: 
        Tuple mit (Gesamtzeit, Zeit von Anfang bis 1. Lichtschranke,
                   Zeit von 1. zur 2. Lichtschranke, Zeit von 2. bis 3. Lichtschranke)
    """      
    global time_tuple                        
    relais.magnet_ein()                             #Schaltet Magnet ein
    time.sleep(0.05)                                #sonst überspringt er wait_for_edge nach mehrern versuchen

    GPIO.wait_for_edge(GPIO_taster, GPIO.FALLING)   #Wartet auf Tasterdruck
    relais.magnet_aus()                             #Schaltet Magnet aus      
    t0 = time.time_ns()
    time.sleep(0.05)                                

    GPIO.wait_for_edge(GPIO_L1, GPIO.RISING )       #Wartet auf 1. Lichtschranke
    t1 = time.time_ns()
    time.sleep(0.05)
    
    GPIO.wait_for_edge(GPIO_L2, GPIO.RISING )       #Wartet auf 2. Lichtschranke
    t2 = time.time_ns()
    time.sleep(0.05)
    
    GPIO.wait_for_edge(GPIO_L3, GPIO.RISING )       #Wartet auf 3. Lichtschranke
    t3 = time.time_ns()

    tges= (t3 - t0) /10**9 -0.015                   #Zeit von Anfag bis Ende, 0.015s sind Korrektur von loslassen des Magneten
    t01 = (t1 - t0) /10**9 -0.015                   #Zeit von Anfang bis 1. Lichtschranke
    t12 = (t2 - t1) /10**9                          #Zeit von 1. zur 2. Lichtschranke
    t23 = (t3 - t2) /10**9                          #Zeit von 2. zur 3. Lichtschranke

    if ausgabe != None:
        print (f"Zeit von Anfag bis Ende (Gesamtzeit) = {tges}")
        print (f"Zeit von Anfang bis 1. Lichtschranke = {t01}")
        print (f"Zeit von 1. zur 2. Lichtschranke =     {t12}")
        print (f"Zeit von 2. zur 3. Lichtschranke =     {t23}")

    return tges,t01,t12,t23 


             


#Debugcode
if __name__ == "__main__":
    pass