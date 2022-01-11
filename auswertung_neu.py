""" Team1 Nördlingen:
auswertung_und_user-interaction.py verarbeitet Benutzereingaben, verarbeitet die ermittelten Messwerte und gibt diese im Terminal und als CSV aus.

Wichtige Funktionen für nachfolgende Programm:
    - wird hinzugefügt

Abkürzungen:
MTM = Massenträgheitsmoment
GRK = Gleitreibungskoeffizient
HRK = Haftreibungskoffeizient
"""

"""
Interne Notizen - werden entfernt:
Wichtiger Hinweis: Code noch nicht mit Pi kompatibel. Muss noch für reale Messung angepasst werden.
"""

test = 0

from zeit import  wait_for_1, mess_zeit_last, wait_for_taster #mess_zeit,

from prettytable import PrettyTable #für Ausgabe als Tabelle im Terminal
# import datetime
# import time
import os
import sys
import math
import datetime
import statistics
# import random
from decimal import Decimal as decimal #für mehr Nachkommastellen

from sensor import init, Ende,motor,winkel, fahr_bis_rutsch
from sensor import mess as mess_zeit



m = 1.03
r = 0.023
g = 9.81
l = 1.2
a = 0
csv_string = ""
time_tuple = ()    


def bogenmass(winkel): #Wandelt Winkel in Bogenmass um
    bogenmass = winkel*(math.pi/180)
    return bogenmass


def create_time_list(anzahl,wiederholungen):
    slist = []
    werte = []
    sum = []
    schnitt_list = []
    material = ["Holz", "Aluminium", "Plastik"]
    for u in range(anzahl):         #anzahl
        sum1 = sum2 = sum3 = sum4 = 0   
        for j in range(wiederholungen): #wiederholungen  für holz öfters
            print(f"Messung {material[u]} in der {j+1} Wiederholung wird durchgeführt.")
            #zeit=(1,2,3,4)
            zeit = mess_zeit()
            # print(zeit)
            sum1+=zeit[0]
            sum2+=zeit[1]
            sum3+=zeit[2]
            sum4+=zeit[3]
        schnitt1 = sum1/wiederholungen
        schnitt2 = sum2/wiederholungen
        schnitt3 = sum3/wiederholungen
        schnitt4 = sum4/wiederholungen

        schnitt_tuple_einzeln = schnitt1, schnitt2, schnitt3, schnitt4
        schnitt_list.append(schnitt_tuple_einzeln)
        
    # print(sstring+"\n")
    # print()
    return schnitt_list

def formel_mtm_theoretisch(): #Theoretische MTM-Formel. Benötigt keinen Übergabewert.
    m = 1.03
    r = 0.023
    mtm_theoretisch = 0.5 * m * (r*r)
    return mtm_theoretisch

def formel_mtm_experimentell(t): #Experimentelle MTM-Formel. Gibt bei übergebener Zeit das MTM zurück.
    global m
    global r
    global g
    global l
    
    var_sin = math.sin(bogenmass(winkel()))
    mtm = ( (2*m*g*var_sin*l) / (math.pow((2*l/t),2)) - m) * (r*r)
    
    print(f"m={m} r={r} g={g} l={l} t={t} winkel={winkel()}")
    
    return mtm

def create_table_hrk(anzahl_pro_winkel):
    header = ['μ-Holz', 'μ-Aluminium', 'μ-Kunststoff']
    table = PrettyTable()
    grk = []
    table.title = 'Messungen Haftreibungskoeffizient'
    table.field_names = header
    material = ["Holz", "Aluminium", "Plastik"]
    csv_table = []
    csv_header = header
    csv_table.append(csv_header)
    global csv_string
    tmp_row = []   
    print(f"Messungen für den Haftreibungskoeffizienten:")
    for j in range(len(header)):       #Für untesrchieldichen Bahnen
        tmp_row.append(mehrere_hfk(anzahl_pro_winkel,material[j]))
    csv_table.append(tmp_row)
    table.add_row(tmp_row)
    csv_string = double_list_to_csv(csv_table)
    write_string_to_file(csv_string, "HRK_Messungen", "HRK")
    print()
    return table

def create_table_grk(anzahl_winkel,anzahl_pro_winkel,Motor_start_winkel=25,Motor_differenz_winkel=5): #Erstellt dynamisch (anzahl an Spalten und Zeilen kann variiert werden(letzteres muss noch optimiert werden) eine Tabelle für das Terminal und CSV)
    header = ['Versuch', 'Winkel in Grad', 'μ-Holz', 'μ-Aluminium', 'μ-Kunststoff']
    table = PrettyTable()
    grk = []
    material = ["Holz", "Aluminium", "Plastik"]
    table.title = 'Messungen Gleitreibungskoeffizient'
    table.field_names = header
    csv_table = []
    csv_header = header
    csv_table.append(csv_header)
    global csv_string
    print(f"Messungen für den Gleitreibungskoeffizienten:")
    for i in range(anzahl_winkel):
        tmp_row = []
        time_list= []
        motor(0)
        motor(Motor_start_winkel+i*Motor_differenz_winkel)
        tmp_row.append(i+1)
        tmp_row.append(f"{winkel():.1f}")
        for j in range(len(header)-2):       #Für untesrchieldichen Bahnen
            tmp_row.append(mehrere_grk(anzahl_pro_winkel,material[j]))
        csv_table.append(tmp_row)
        table.add_row(tmp_row)
        csv_string = double_list_to_csv(csv_table)
    write_string_to_file(csv_string, "GRK_Messungen", "GRK")
    #     retValue = table
    print()
    return table

def create_table_mtm(anzahl_winkel,anzahl_pro_winkel,Motor_start_winkel=12,Motor_differenz_winkel=2): #Erstellt dynamisch (anzahl an Spalten und Zeilen kann variiert werden(letzteres muss noch optimiert werden) eine Tabelle für das Terminal und CSV)
    header = ['Versuch', 'Winkel', 'MTM-Holz', 'MTM-Holz-Kor.' ,'MTM-Aluminium', 'MTM-Alu-Korr.', 'MTM-Kunststoff', 'MTM-Kunst-Kor.' ,'MTM-Theoretisch']
    table = PrettyTable()
    csv_table = []
    title = 'Messungen Massenträgheitsmoment in g*m^2'
    table.title = title
    #csv_table.append[title]    #Warum=???
    table.field_names = header
    csv_table.append(header)
    global csv_string
    print(f"Messungen für das Massenträgheitsmoment:")
    for i in range(anzahl_winkel):
        tmp_row = []
        time_list= []
        motor(0)
        motor(Motor_start_winkel+i*Motor_differenz_winkel)
        time_list = create_time_list((3),anzahl_pro_winkel)
        tmp_row.append(i+1)
        tmp_row.append(f"{winkel():.1f}")
        
        for j in range(len(time_list)):
            mtm_val = 1000*formel_mtm_experimentell(time_list[j][0])
            mtm_val_corr = 1000*Massentragheitsmoment_korrektur(time_list[j],j)
            tmp_row.append(f"{mtm_val:.6f}")
            tmp_row.append(f"{mtm_val_corr:.6f}")
            # print(f"Messung {i+1,j+1} wurde durchgeführt. MTM: {mtm_val}")
        mtm_theoretisch = formel_mtm_theoretisch()
        mtm_theo = mtm_theoretisch*1000
        tmp_row.append(f"{mtm_theo:.6f}")
        csv_table.append(tmp_row)
        #print(tmp_row)
        table.add_row(tmp_row)
        # print(str(table) + '\n')
    csv_string = double_list_to_csv(csv_table)
    write_string_to_file(csv_string, "MTM_Messungen", "MTM")
    print()
    return (table)

def Massentragheitsmoment_korrektur(time_tuple,j):
    werte=[0.0075,0.0128,0.0103]

    mü=werte[j]
    m=1.0299
    r=0.023
    t=time_tuple[0]
    g=9.81
    l=1.2
    winkel1 = winkel()
    bogenmaß = winkel1*(math.pi/180)#winkel()*(math.pi/180)
    delta_energy = mü*m*g*math.cos(bogenmaß)*l
    
    #mtm = ((((2*((m*g*math.sin(bogenmaß)*l)-delta_energy))/((2*l)/t)**2)-m)*r**2      #-(mü*m*g*math.cos(bogenmaß)*l)
    mtm = (((2*(m*g*math.sin(bogenmaß)*l-delta_energy))/((2*l)/t)**2)-m)*r**2
    #log.debug(f"MTM_korrektur berechnet mit m={m} r={r} g={g} l={l} t={t} winkel={winkel1} mtm={mtm}")
    return mtm

def double_list_to_csv(list): #Konvertiert Tabelle in einen CSV-String
    sstring = ""
    for i in range(len(list)):
        # print(len(list[0]))
        for j in range(len(list[0])):
            sstring += str(list[i][j])
            j = j + 1
            if j < len(list[0]):
                sstring += ";"
        sstring += "\n"
    return sstring

def add_values_to_csv_string(value):
    global csv_string
    csv_string += value + ";" + "\n"

def formel_gleitreibungskoeffizient(): #Formel Gleitreibungskoeffizient
    beschleunigung = 0
    time_list=mess_zeit()
    l=1.06
    t=(time_list[-1]+time_list[-2])
    beschleunigung = (2 * l) / (math.pow(t, 2))
    global g
    grk_winkel = winkel()
    grk = math.tan(bogenmass(grk_winkel)) - (beschleunigung/g*math.cos(bogenmass(grk_winkel)))
    #print(f"t={t} a={beschleunigung} g={g} winkel={grk_winkel} grk={grk}")
    return grk

def formel_haftreibungskoeffizient(): #Formel Haftreibungskoffezient
    hrk_winkel = 0    
    fahr_bis_rutsch()
    hrk_winkel = winkel()
    hrk = math.tan(bogenmass(hrk_winkel))
    return hrk

def mehrere_hfk(anzahl,material):
    hfk_list = []
    # print(f"Messungen für den Haftreibungskoeffizienten")
    for i in range(anzahl):
        print(f"Messung {material} wird in der {i+1} Wiederholung durchgeführt, Material ausrichten un Taster betätigen um fortzufahren")
        motor(0)
        wait_for_taster()
        wert= formel_haftreibungskoeffizient()
        hfk_list.append(wert)
    motor(0)
    #print (f"Durschnittswert = {statistics.mean(hfk_list)}")  
    return statistics.mean(hfk_list)

def mehrere_grk(anzahl,material):
    grk_liste = []
    # print(f"Messungen für den Gleitreibungskoeffizienten")
    for i in range(anzahl):
        print(f"Messung {material} wird in der {i+1} Wiederholung durchgeführt")
        wert = formel_gleitreibungskoeffizient()        
        grk_liste.append(wert)
    print (f"Durschnittswert = {statistics.mean(grk_liste)}")    
    return statistics.mean(grk_liste)  

def write_string_to_file(string, dateiname, typ_messung): #Geändert!!! Änderung beachten!!!!
    current_time = str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    user_dir = os.path.expanduser("~/")
    working_sub_dir_1 = "projekt"

    working_dir_1 = os.path.join(user_dir, working_sub_dir_1)
    if os.path.isdir(working_dir_1) == False:
        os.mkdir(working_dir_1)

    working_sub_dir_2 = "CSVs_Messungen"
    working_dir_2 = os.path.join(working_dir_1, working_sub_dir_2)
    if os.path.isdir(working_dir_2) == False:
        os.mkdir(working_dir_2)

    working_dir_3 = os.path.join(working_dir_2, str(typ_messung))
    if os.path.isdir(working_dir_3) == False:
        os.mkdir(working_dir_3)

    full_working_dir = working_dir_3
    filename = f"{dateiname}_{current_time}.csv"
    full_file_path = os.path.join(full_working_dir, filename)
    with open(full_file_path, 'w') as f:
        f.write(str(string))

def print_mtm(anzahl_winkel,anzahl_pro_winkel,Motor_start_winkel,Motor_differenz_winkel): #Hier noch Übergabewerte anpassen, und in den Funktionsteilen
    print()
    print(create_table_mtm(int(anzahl_winkel),int(anzahl_pro_winkel),float(Motor_start_winkel),float(Motor_differenz_winkel))) #Hier noch Übergabewerte anpassen, und in den Funktionsteilen
    #create_table_mrk(Anzahl verschiedener Winkel,Anzahl pro Winkel, Startwinkel, Differenzwinkel))
    print()
    #print('-'*100)
    
def print_grk(anzahl_winkel,anzahl_pro_winkel,Motor_start_winkel,Motor_differenz_winkel): #Hier noch Übergabewerte anpassen, und in den Funktionsteilen
    print() 
    print(create_table_grk(int(anzahl_winkel),int(anzahl_pro_winkel),float(Motor_start_winkel),float(Motor_differenz_winkel)))#Hier noch Übergabewerte anpassen, und in den Funktionsteilen
    #create_table_mrk(Anzahl verschiedener Winkel,Anzahl pro Winkel, Startwinkel, Differenzwinkel))
    print()
    #print('-'*100)

def print_hrk(anzahl_pro_winkel): #Hier noch Übergabewerte anpassen, und in den Funktionsteilen
    print()
    print(create_table_hrk(int(anzahl_pro_winkel))) #Hier noch Übergabewerte anpassen, und in den Funktionsteilen
    print()
    #print('-'*100)

def fehlerhafte_eingabe():
    inp = input("Fehlerhafte Eingabe. Programm erneut starten? (y/n) ")
    if inp == 'y' or 'Y' or 'J' or 'j':
        f_user_interaction()
    if inp == 'n' or 'N':
        print("Programm wird beendet.")
        sys.exit()
    else:
        print("Erneut fehlerhafte Eingabe. Programm wird beendet.")
        sys.exit()

def f_user_interaction(): #Methode für die Nutzereingaben
    sstring = f"Bitte Funktionalität angeben:\n"
    optionen = []
    init()
    optionen.append('Gleitreibungskoeffizient ermitteln')
    optionen.append('Haftreibungskoeffizient ermitteln')
    optionen.append('Massenträgheitsmoment ermitteln')
    for i in range(len(optionen)):
        sstring += f"{i+1}. {optionen[i]}\n"
    inp = input(sstring)
    if inp == "1": #GRK
        anzahl_winkel =  input("Anzahl verschiedener Winkel eingeben. ")
        anzahl_pro_winkel =  input("Anzahl pro Winkel eingeben. ")
        Motor_start_winkel = input("Startwinkel eingeben. ")
        Motor_differenz_winkel = input("Differenzwinkel eingeben. ")
        print_grk(anzahl_winkel,anzahl_pro_winkel,Motor_start_winkel,Motor_differenz_winkel)
        # create_table_grk(anzahl_winkel, anzahl_pro_winkel)
    elif inp == "2":#HRK
        anzahl_pro_winkel =  input("Anzahl pro Winkel eingeben. ")
        print_hrk(anzahl_pro_winkel)
    elif inp == "3": #MTM
        anzahl_winkel = input("Anzahl verschiedener Winkel eingeben. ")
        anzahl_pro_winkel = input("Anzahl pro Winkel eingeben. ")
        Motor_start_winkel = input("Startwinkel eingeben. ")
        Motor_differenz_winkel = input("Differenzwinkel eingeben. ")
        print_mtm(anzahl_winkel,anzahl_pro_winkel,Motor_start_winkel,Motor_differenz_winkel)
    else:
        fehlerhafte_eingabe()
        
    # pass
    """
        1.  Gleitreibung
            -Startwinkel eingeben (standart 25)
            -differnetz winkel  (standart 5)
            -Anzahl verschiedener Winkel
            -Anzahl pro Winkel
            create_table_grk(Anzahl verschiedener Winkel,Anzahl pro Winkel, Startwinkel, Differenzwinkel))


        2.  Haftreibung
            -Wie viele wiederholungen
            create_table_hrk(wiederholungen)


        3.Rollreibung

        4. MTM Messung?? denk du hast das gemeint  
            -Startwinkel eingeben (standart 12)
            -differnetz winkel  (standart2)
            -Anzahl verschiedener Winkel
            -Anzahl pro Winkel
            create_table_mrk(Anzahl verschiedener Winkel,Anzahl pro Winkel, Startwinkel, Differenzwinkel))  
    """
        



if __name__ == "__main__":
    # init()
    # motor(0)n
    #motor(36)
    #print(mehrere_grk(3))
    #print(formel_gleitreibungskoeffizient())
    #print(formel_haftreibungskoeffizient())
    #print(create_table_dyn(1,1))
    #print(create_table_grk(2,2))
    f_user_interaction()
    # Ende()
    pass

    