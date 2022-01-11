""" Team1 Nördlingen:
sensor.py ist das Verbindungsglied zwischen den einzelnen Sensoren und Aktuatoren

Wichtige Funktionen für nachfolgende Programme:
    -init()                 Initialisiert alle Sensoren, schaltet Aktuatoren aus
                            muss zu Programmanfang 1x ausgefürht werden

    -motor(Winkel)          Steuert den Motor, 
                            -übergabe 0 führt zur Referenzfahrt
                            -übergabe !=0 fährt den angegebenen Winkel an
                            -Rückgabewert = aktueller Winkel

    -winkel(schritte)       Gibt winkel der Schiefen ebene zurück. 
                            Übergabeparameter =schritte vom rotary Encoder, wenn nichts übergeben, wird aktuelle Schrittzahl verwendet

    -mess(Ausgabge)         Startet den Messzyklus
                            gibt als Rückgabewert ein Tupel mit den einzelen Messwerten zurück
                            retVal = (Gesamtzeit, Zeit von Anfang bis 1. Lichtschranke, Zeit von 1. zur 2. LS, Zeit von 2. bis 3. LS (ENDE))
                            Wenn Ausgabe =! None ist werden die Messwerte in der Konsole ausgegeben

    -Ende()                 Beendet alles, schaltet Aktuatoren aus
"""

import time
import relais
import zeit
import rotary
import RPi.GPIO as GPIO


schritte = 0        #Hier werden die Schritte gespeicher, die sich der Rotary Encoder ausfdreht
richtung = 0        #Richtung ob Motor aus oder einfährt, +1 = ausfahren -1 = einfahren

def init():
    """Ruft die Init-Funktionen der Unterprogramm auf.
       Hält den Motor an.
       Schaltet den Magnet aus.
       Aktiviert den Interrupt des Rotary Encoders.

    Args: 
        None
    Return: 
        None
    """                                 
    zeit.init_port()                    #Ruft die Init-Funktionen auf
    relais.init_port()
    rotary.init_port(callback_rotary)   #Ruft die Init-Funktion vom Rotary Encoder Programmteil auf, übergabe ist die Funktion, die bei Interrupt ausgeführt werden soll
    relais.motor_stop()                 #Hält Motor an
    relais.magnet_aus()                 #Schaltet Magnet aus
    rotary.ein()                        #Aktiviert den Interrupt des Rotary Encoders


def callback_rotary(channel):
    """Funktion wird bei jedem Interrupt vom Rotary Encoder aufgerufen.
       Zählt die Schritte Hoch oder Runter, je nachdem ob der Motor aus oder einfährt.

    Args: 
        channel von dem der Interrupt aufgerufen wird
    Return: 
        None
    """          
    global schritte, richtung    
    schritte += richtung                #Zählt entweder hoch oder runter, je nach Richtung vom Motor
    #print(schritte)                    #Wenn Auskommentierung entfernt Ausgabe des aktuellen Schrittes bei Änderung vom Schritt

def mess():
    """Startet den Messzyklus.

    Args: 
        None
    Return: 
        Tuple mit (Gesamtzeit, Zeit von Anfang bis 1. Lichtschranke,
                   Zeit von 1. zur 2. Lichtschranke, Zeit von 2. bis 3. Lichtschranke) 
    """   
    zeiten = zeit.mess_zeit()                                  #Übergabe von !=None für ausgabe der Messwerte, None == keine Ausgabe
    return zeiten

  
def motor(pos):
    """Entscheidet ob Referenzfahrt oder Positionsfahrt gestartet wird.

    Args: 
        pos = 0 
           -> Referenzfahrt
        pos zwischen 12 und 36
           -> fährt übergebenen Winkel an.
    Return: 
        angefahren Winkel 
    """   
    if pos == 0:
        motor_init()                    #Referenzfahrt wird aufgerufen
        retVal = winkel()
    elif pos >= 12 and pos <=36:
        motor_angle(pos) 
        retVal = winkel()               #Positionsfahrt wird aufgerufen
    else:
        print(f"Bitte 0 für Refferenzfahrt bzw Wert zwischen 12 und 36 Grad eingeben. {pos} eingegeben")
        retVal = None
    
    return retVal


def motor_init():
    """Führt Referenzfahrt aus.

    Motor wird solange eingefahren bis sich die Schritte vom Rotary-Encoder 2s nicht mehr ändern

    Args: 
        None
    Return: 
        None
    """   
    global richtung,schritte,schritte_last
    richtung = -1                               #-1 da Motor einfährt
    schritte = schritte_last = 0                #Setzt die Schritte zurück
    relais.motor_ein()                          #Motor wird eingefahren
    time_last = time.time()                     #Startzeit wird gesetzt

    while time.time() <= time_last+2:           #Fährt so lange ein bis sich der Rotary Encoder 2s nicht mehr bewegt
        if schritte != schritte_last:           #Abfrage ob sich die Schritte Geändert haben
            schritte_last = schritte            #Fall schritte geändert, Zeit zurücksetzen
            time_last = time.time()           

    relais.motor_stop()                         #Hält Motor an
    schritte = 0                                #Setzt Schritte auf 0 für komplett eingefahren
    richtung = 0                                #Setzt Richtung auf 0 das bei Erschütterungen der Ebene sich der Winkel nicht mehr ändert
    

def motor_angle(req_angle):
    """Führt Positionsfahr aus.

    Erst wird unterschieden, ob der Winkel größer oder kleiner als der aktuelle Winkel ist, also ob der Motor ein oder ausfahren muss.
    Dann wird berechnet wie weit die Differenz zwischen aktuellem Winkel und Winkel wenn der Motor einen Schritt weiter fahren würde ist.
    Wenn es besser ist einen Schritt weiter zu fahren, wird der Motor so lange fahren, bis es sich nicht mehr rentiert einen Schritt
    weiter zu fahren. Außerdem wird das fahren auch beendet wenn sich 2s lang der Motor nicht mehr bewegt.

    Args: 
        req_angle = Angeforderter Winkel der Schiefen Ebene
    Return: 
        None
    """   
    global richtung,schritte,schritte_last

    if req_angle > winkel():                                    #Wenn gewünschter Winkel größer als akt. Winkel ->ausfahren
        delta_now = abs(req_angle - winkel(schritte))           #aktuelle Differenz zwischen angefordertem Winkel und aktuellem Winkel
        delta_next = abs(req_angle - winkel(schritte +1))       #Differenz zwischen angefordertem Winkel und Winkel wenn Motor einen Schritt weiter ausfährt
        richtung = 1                                            #Richtung =1 für Ausfahren
        relais.motor_aus()
        time_last = time.time()

        while (delta_now > delta_next) and time.time() <= time_last+2:        #Fährt so lange aus bis es sich nicht mehr rentiert auszufahren oder sich die Schritte 2s nicht ändern
            delta_now = abs(req_angle - winkel(schritte))                     #Berechnet wieder Differenz zwischen angefordertem Winkel und aktuellem Winkel
            delta_next = abs(req_angle - winkel(schritte +1))
            if schritte != schritte_last:                                     #Abfrage ob sich die Schritte unterscheiden zum letzen mal
                schritte_last = schritte                                      #Letzten Schritte mit aktuellen Schritten überschreiben
                time_last = time.time()                                       #Zeit zurücksetzen

    elif req_angle < winkel():                                  #Wenn gewünschter Winkel kleiner als akt.Winkel ->einfahren
        delta_now = abs(req_angle - winkel(schritte))           #aktuelle Differenz zwischen angefordertem Winkel und aktuellem Winkel
        delta_next = abs(req_angle - winkel(schritte -1))       #Differenz zwischen angefordertem Winkel und Winkel wenn Motor einen Schritt weiter einfährt
        richtung = -1                                           #Richtung =-1 für Einfahren
        relais.motor_ein()
        time_last = time.time()

        while (delta_now > delta_next) and time.time() <= time_last+2:         #Fährt so lange ein bis es sich nicht mehr rentiert einzufahren oder sich die Schritte 2s nicht ändern
            delta_now = abs(req_angle - winkel(schritte))                      #Berechnet wieder Differenz zwischen angefordertem Winkel und aktuellem Winkel
            delta_next = abs(req_angle - winkel(schritte -1))
            if schritte != schritte_last:                                      #Abfrage ob sich die Schritte unterscheiden zum letzen mal
                schritte_last = schritte                                       #Letzten Schritte mit aktuellen Schritten überschreiben
                time_last = time.time()                                        #Zeit zurücksetzen

    relais.motor_stop()                                          #Motor anhalten
    richtung = 0                                                 #Setzt Richtung auf 0 das bei Erschütterungen der Ebene sich der Winkel nicht mehr ändert

def winkel(x = None):
    """Rechnet die Schritte des Rotary Encder in den Winkel der Schiefen Ebene um.

        Wenn nichts übergeben wurde, wird der aktuelle Winkel zurückgegeben
        Wenn was übergeben wurde, wird der Wert als Schritte angenommen und aus ihm der Winkel berechnet

    Args: 
        x = Schritte (optional)
    Return: 
        aktueller Winkel in Grad
    """
    global schritte
    if x == None:               #Abfrage ob was übergeben wurde     
        x=schritte              #Wenn keine Schritte übergeben wurden wird aktueller Winkel ausgerechnet

    return 0.0000000000282*x**6 - 0.0000000010803*x**5 - 0.0000006752755*x**4 + 0.0000950995362*x**3 - 0.0060519860405*x**2 + 0.4723307728188*x + 12.2791237950985

def fahr_bis_rutsch():
    """Fährt so lange den Motor hoch bis die erste Lichtschranke unterbrochen wird.

    Args: 
        None
    Return: 
        Winkel bei dem die Lichtschranke unterbrochen wurde
    """   
    global richtung
    richtung = 1                #=1 für Ausfahren
    relais.motor_aus()
    zeit.wait_for_1()           #Wartet bis 1. Lichtschranke durchbrochen wird
    return(winkel())    


def Ende():
    """Brint alles wieder in Ausgangsstellung

    Args: 
        None
    Return: 
        None
    """   
    relais.motor_stop()         #Hält Motor an
    relais.magnet_aus()         #Schaltet Magnet aus
    rotary.aus()                #Schaltet Interrupt vom Rotary Encoder aus
    GPIO.cleanup()              #Bringt alle GPUIs wieder in Ausgangsstellung (Eingänge)


#Debug Code
if __name__ == "__main__":
    
    #global schritte

    init()
    relais.motor_aus()
    stop
    #motor(0)
    #motor(30)
    #print(winkel())
    #stop
    #stop
    for i in range(12,36,6):
        motor(0)
        motor(i)
        print(winkel())
        input('weiter')
   # stop
    #print(schritte)
    #richtung = 1
    for i in range(0,100,10):
        motor(0)
        richtung=1
        relais.motor_aus()

        while schritte<i:
            #print("gefangen")
            pass
        relais.motor_stop()
        
        print(f"aktuelle schritte= {schritte} alter winkel = {winkel(schritte)} neuer Winkel {Winkel_neu(schritte)}")
        input("messung")

    stop
    def save(werte):
        datei = open('log.log','a')
        datei.write(f"{winkel(schritte)};{werte[0]};{werte[1]};{werte[2]};{werte[3]}\n")
        datei.close()

    try:
        init()
        motor_init()
        motor(20)
        for i in range(14,36):
            motor_angle(i)            
            save(mess())

        #motor(14)
        #print(winkel(schritte))
        #mess()
    finally:
        Ende()







