#MySQL Server Zugriff
import mysql.connector
import configmysql      #Server Verbindungsdaten
import os               #nfc-poll Befehl über System
from tkinter import *
from tkinter import messagebox
import time

class Fullscreen_Window:

    def __init__(self):
        self.tk = Tk()
        self.tk.columnconfigure(0, weight=1)
        self.tk.columnconfigure(1, weight=1)
        self.tk.rowconfigure(0, weight=1)
        self.tk.attributes('-fullscreen', True)  # Skaliert das erstellte Fenster direkt auf Vollbild
        self.state = True
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Umschalten zwischen Vollbild und Maximiert
        self.tk.overrideredirect(False)
        self.tk.wm_attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.overrideredirect(False)
        self.tk.wm_attributes("-fullscreen", False)
        return "break" 


if __name__ == '__main__':

    #Verbindung MySQL herstellen
    def datenbank():
        try:
            cnx = mysql.connector.connect(**configmysql.configserver)
        except:
            messagebox.showwarning("WARNUNG", "Keine Verbindung zur Datenbank!")
        cursor = cnx.cursor()
        cursor.execute("select RFID from user")
        rfid_list = cursor.fetchall()
        rfid_list = [i[0] for i in rfid_list]
        return rfid_list


    #Boolsche Variable zur Anzeige Bestellung oder Screensaver
    switch_gui = False

    scr_saver = Fullscreen_Window()
    scr_saver.tk.title("Kühlschrankmanagement 3000 - Bildschirmschoner")

    def shutdown():
        button_shutdown.flash()
        os.system("sudo shutdown -h now")

    def restart():
        button_restart.flash()
        os.system("sudo reboot")
    
    button_shutdown = Button(scr_saver.tk, relief = "ridge", bd = 4, text = "Aus-die-Maus", command = shutdown, font = "Arial 14")
    button_shutdown.pack(padx = 5, pady = 5)

    button_restart = Button(scr_saver.tk, relief = "ridge", bd = 4, text = "Poweronov", command = restart, font = "Arial 14")
    button_restart.pack(padx = 5, pady = 5)

    fsei_logo = PhotoImage(file = "/home/pi/Schreibtisch/piGUI_KM3000/Code/FSEI_Logo_15.png")
    fsei_logo = fsei_logo.subsample(2)
    label_logo = Label(scr_saver.tk, image = fsei_logo)
    label_logo.image = fsei_logo
    label_logo.pack(fill = BOTH, expand = 1, padx = 5, pady = 5)
    
    uhr = Label(scr_saver.tk,
            font = ('Arial', 68),
            fg = "#81197F") #Fakultätsfarbe

 
    zeit = ''

    def tick():
        global zeit
        neuezeit = time.strftime('%H:%M')
        if neuezeit != zeit:
            zeit = neuezeit
            uhr.config(text = zeit) 
        uhr.after(200, tick) 
 
    tick()

    rfid_frame = Frame(scr_saver.tk, relief = "ridge", bd = 5)
    
    def bar():
        button_bar.flash()
        log = open("log.txt", "w")
        log.write("12:34:56:78")
        log.close()
        hint = Fullscreen_Window()
        hint.tk.title("INFO")
        message1 = Message(hint.tk, text = "\nBitte schmeiß das Geld\nins orangene\n\nSparschwein\n\n\n\nDANKE!", font = "Arial 36", padx=20, pady=20, justify = "center", anchor = "center")
        message2 = Message(hint.tk, text = "\nUnd nicht vergessen:\nIns orangene\n\nSparschwein\n\n\n\nDANKE!", font = "Arial 36", padx=20, pady=20, justify = "center", anchor = "center")
        message1.pack()
        hint.tk.update()
        time.sleep(1.5)
        os.system('/usr/bin/python3 /home/pi/Schreibtisch/piGUI_KM3000/Code/piGUI.py')
        message1.destroy()
        message2.pack()
        hint.tk.update()
        time.sleep(2)
        hint.tk.destroy()

        
    def display_rfid(rfid):
        messagebox.showinfo("RFID", "Deine NFC-ID lautet:\n%s\nLass diese ID über den Kassier (Alex) in die Datenbank eintragen!"%rfid)

    def read_rfid():
        button_readrfid.flash()
        rfid_list = datenbank()
        reading = Fullscreen_Window()
        reading.tk.title("INFO")
        reading.tk.update()
        message = Message(reading.tk, text = "Bitte Karte auf NFC-Feld legen.\n\nDeine Daten werden ausgelesen...\n\nGuthaben wird abgebucht...", font = "Arial 36", padx=20, pady=20, justify = "center", anchor = "center")
        message.pack()
        reading.tk.update()
        try:
            nfc = os.popen("nfc-poll | awk -F: '$1 ~ /UID/ {print $2; }'").readlines()
        except:
            messagebox.showwarning("WARNUNG", "NFC-Reader nicht gefunden!")
        if nfc:
            nfc = [x.strip(' ') for x in nfc]
            rfid = ':'.join(nfc[0].split())
            #RFID mit Datenbank vergleichen
            for value in rfid_list:
                if value == rfid:
                    switch_gui = True
                    log = open("/home/pi/Schreibtisch/piGUI_KM3000/log.txt", "w")
                    log.write(rfid)
                    log.close()
                    #scr_saver.tk.withdraw()
                    try:
                        os.system('/usr/bin/python3 /home/pi/Schreibtisch/piGUI_KM3000/Code/piGUI.py')
                        reading.tk.destroy()
##                        scr_saver.tk.update()
##                        scr_saver.tk.deiconify()
                    except:
                        print("Fehler")
                    break
                else:
                    switch_gui = False
                    if os.path.isfile("log.txt"):
                        os.remove("log.txt")
            if switch_gui == False:
                reading.tk.destroy()
                display_rfid(rfid)
##        scr_saver.tk.after(200, read_rfid)
        else:
            reading.tk.destroy()

    button_readrfid = Button(rfid_frame, relief = "ridge",overrelief = "sunken", bd = 5, text = "Karte einlesen", bg = "#81197F", fg = "black", activebackground = "#81197F", command = read_rfid, font = "Arial 28")
    button_readrfid.pack(side = LEFT, padx = 2)
    button_bar = Button(rfid_frame, relief = "ridge",overrelief = "sunken", bd = 5, text = "BAR", bg = "#81197F", fg = "black", activebackground = "#81197F", command = bar, font = "Arial 28")
    button_bar.pack(side = LEFT, padx = 2)
    rfid_frame.pack()
    uhr.pack(fill = BOTH, expand = 1, padx = 5, pady = 5)
##    scr_saver.tk.after(200, read_rfid)
    scr_saver.tk.mainloop()

