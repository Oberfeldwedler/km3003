#MySQL Server Zugriff
import mysql.connector
import configmysql      #Server Verbindungsdaten
import os
from tkinter import *
from tkinter import messagebox
from collections import OrderedDict
from operator import itemgetter
import time
import math

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

class item:

    def __init__(self, id, bezeichnung, preis, master_frame, height_f, width_f):
        self.id = id    
        self.bezeichnung = bezeichnung
        self.preis = preis
        self.counter = IntVar()
        self.master_frame = master_frame
        self.height_f_button = height_f
        self.width_f_button = width_f
        #Dimensionierung Button
        height_button = height_f_button-10
        width_button = width_f_button-20

        #Hack Spezi
        if self.id == "D" and self.bezeichnung=="Spezi":
            bezeichnung = "Altes Spezi"
            preis = 0.0
            self.preis = 0.0
            
        #Aktion Button
        def click():
            #Hack Spezi
            if self.id == "D" and self.bezeichnung=="Spezi":
                return
            
            self.counter.set(self.counter.get() +1)
            preis_list.append(self.preis)
            gesamt_preis_text.set("Buchen: " + str(round(sum(preis_list),1)) + Euro)

        #GUI-Elemente anlegen
        self.frame_button = Frame(master = master_frame, borderwidth = 1, relief = 'ridge', height = self.height_f_button, width = self.width_f_button)
        self.item_button = Button(self.frame_button, relief = 'ridge', text = bezeichnung + "\n" + str(preis) + Euro, font = "Arial 14", command = click, compound = 'center')
        self.item_button.config(image = button_bg, width = width_button, height = height_button)
        self.item_label = Label(master = self.frame_button, text = self.counter.get(), textvariable = self.counter, font = "Arial 14",)
        self.frame_button.grid_propagate(0)
        self.item_button.grid_propagate(0)
        self.item_label.grid_propagate(0)
        self.item_button.grid()
        self.item_label.place(relx=1, rely = 1, x=-2, y=-2, anchor=SE)

        # Hack Spezi
        if self.id == "D" and self.bezeichnung == "Spezi":
            self.item_button["state"] = DISABLED

class SimpleTable(Frame):

    def __init__(self, parent, rows=4, columns=2):
        Frame.__init__(self, parent, bg="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Label(self, text="%s/%s" % (row, column), 
                                 borderwidth=0, width=10)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

if __name__ == '__main__':

    #Verbindung MySQL herstellen
    try:
        cnx = mysql.connector.connect(**configmysql.configserver)
    except:
        messagebox.showwarning("WARNUNG", "Keine Verbindung zur Datenbank!")
    cursor = cnx.cursor()

    log = open("log.txt", "r")
    user_rfid = log.readline()
    log.close()
    if os.path.isfile("log.txt"):
        os.remove("log.txt")

    cursor.execute("select * from user where RFID = '%s'"% user_rfid)
    sql_user = cursor.fetchall()
    user_id = sql_user[0][0]
    #Statistik des Users auslesen
    cursor.execute("select * from stats where SQL_Stats_ID like '_%s'"% user_id)
    user_stats = cursor.fetchall()
    #Statsitik sortieren nach größter Anzahl
    user_stats.sort(key=itemgetter(3), reverse = True)

    
    #Aufbereitung Daten
    aktuell_kst = float(sql_user[0][5])
    uebertrag = float(sql_user[0][10])
    zu_zahlen_betrag = aktuell_kst+uebertrag
    name = sql_user[0][3] + ' ' + sql_user[0][2]
    jahr_anzahl = sql_user[0][6]
    total_anzahl = sql_user[0][8]
    kuchen = sql_user[0][11]
    if kuchen >= 1:
        kuchen_color = "red"
        kuchen_font = "Arial 12 bold"
        kuchen_popup_meldung = True
    else:
        kuchen_color = "black"
        kuchen_font = "Arial 12"
        kuchen_popup_meldung = False

    Euro = "0\u20AC"

#GUI:
    
    #Fullscreen Window Layout
    gui = Fullscreen_Window()
    gui.tk.title("Kühlschrankmanagement 3000")
    gui.tk.update()
    frame1 = Frame(gui.tk, borderwidth = 4, relief = 'ridge', width = (gui.tk.winfo_width()/4)*3)
    frame1.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = "nsw")
    frame1.update()
    frame2 = Frame(gui.tk, borderwidth = 4, relief = 'ridge', width = gui.tk.winfo_width()/4)
    frame2.grid_propagate(0)
    frame2.grid(column = 1, row = 0, padx = 5, pady = 5, sticky = "nse")
    frame2.update()


    #Kuchenmeldung
    def kuchen_popup(kuchen):
        messagebox.showwarning("WARNUNG", "Du hast noch %s Kuchen mitzubringen!!!"%str(kuchen))
        

    if kuchen_popup_meldung == True:
        kuchen_popup(kuchen)

    #Variablen für die Widgets
    height_items = int(((frame1.winfo_height()-15)/6)*5)   #4 borderwidth frame1 + 5 padding frame1 + 2*1 borderwidth frame_items + 2*2 padding frame_items
    width_items = int(frame1.winfo_width()-24)                  #2*4 borderwidth frame1 + 2*5 padding frame1 + 2*1 borderwidth frame_items + 2*2 padding frame_items
    height_choice = int((frame1.winfo_height()-15)/6)
    width_choice = width_items
    #Einteilung frame1
    frame_items = Frame(frame1, borderwidth = 1, relief = 'ridge', height = height_items, width = width_items)
    frame_items.grid_propagate(0)
    frame_items.grid(column = 0, row = 0, padx = 2, pady = 2)
    frame_items.update()
    frame_choice = Frame(frame1, borderwidth = 1, relief = 'ridge', height = height_choice, width = width_choice )
    frame_choice.grid_propagate(0)
    frame_choice.grid(column = 0, row = 1, padx = 2, pady = 2)
    frame_choice.update()

    #Anzahl items auslesen
    cursor.execute("select count(*) from items")
    items_rows = cursor.fetchone()

    #Laufvariable Anzahl Angebote
    items_count = items_rows[0]

    #Skalierung für Buttons
    scale_items = int(math.ceil(items_count/4))
    #  - Variablen
    height_f_button = int((frame_items.winfo_height()-15)/scale_items)
    width_f_button = int((frame_items.winfo_width()-10)/4)
    height_button = height_f_button-10
    width_button = width_f_button-10
    #  - Transparentes Buttonimage zur Skalierung in Pixeln
    button_bg = PhotoImage(file = "/home/pi/Schreibtisch/piGUI_KM3000/Code/button_bg.png") 

    #ITEMS
    #Spalte und Reihe initialisieren
    column_frame_button = 0
    row_frame_button = 0
    #Array-Zähler
    items_list_i = 0

    #Alle items auslesen
    cursor.execute("select * from items")
    items_list = cursor.fetchall()

    #leeres Dict zur Verwaltung anlegen und füllen
    items_dict = OrderedDict()
    for i in range(1,items_count+1):
        items_dict["item_%s"% str(i)] = item(items_list[items_list_i][0], items_list[items_list_i][1], items_list[items_list_i][3], frame_items, height_f_button, width_f_button)
        items_list_i +=1
        items_dict["item_%s"% str(i)].frame_button.grid(column = column_frame_button, row = row_frame_button, padx = 1, pady = 1)
        column_frame_button +=1
        if column_frame_button > 3:
            row_frame_button += 1
            column_frame_button = 0

    #VERWALTUNGSBUTTONS
    #Skalierung für Verwaltungsbuttons
    height_ch_f_button = int(frame_choice.winfo_height()-5)
    width_ch_f_button = int((frame_choice.winfo_width()-8)/3)
    height_ch_button = height_ch_f_button-10
    width_ch_button = width_ch_f_button-10

    #Funktionen der Buttons    
    def abbrechen():
        gui.tk.destroy()

    def reset():
        for item_i in items_dict:
            items_dict[item_i].counter.set(0)
        del preis_list[:]
        gesamt_preis_text.set("Buchen: " + str(float(sum(preis_list))) + Euro)

    def buchen():
        confirm = Fullscreen_Window()
        confirm.tk.title("INFO")
        confirm.tk.update()
        Message(confirm.tk, text = "Füll bitte den Kühlschrank wieder auf, Schätzelein!\n\nAch ja, und: Dein Flug wurde gebucht\n;)", font = "Arial 52", padx=20, pady=20, justify = "center", anchor = "center").pack()
        confirm.tk.update()
        confirm.tk.after(3500, confirm.tk.destroy)
        for item_i in items_dict:
            anzahl = items_dict[item_i].counter.get()
            item_id = items_dict[item_i].id
            preis = items_dict[item_i].preis
            sql_stats_id = item_id+user_id
            akt_kst = anzahl*preis
            cursor.execute("select Anzahl from stats where SQL_Stats_ID = '%s'"% sql_stats_id)
            anzahl_akt_item = cursor.fetchone()
            anzahl_gesamt_item = anzahl_akt_item[0]+anzahl
            cursor.execute("select Aktuell_anz, Aktuell_kst, Jahr_anz, Jahr_kst, Total_anz, Total_kst from user where SQL_User_ID = '%s'"% user_id)
            user_data = cursor.fetchall()
            aktuell_anz_user = user_data[0][0]
            aktuell_kst_user = user_data[0][1]
            jahr_anz_user = user_data[0][2]
            jahr_kst_user = user_data[0][3]
            total_anz_user = user_data[0][4]
            total_kst_user = user_data[0][5]
            #print(aktuell_anz_user, aktuell_kst_user, jahr_anz_user, jahr_kst_user, total_anz_user, total_kst_user)
            try:
                cursor.execute("UPDATE stats SET Anzahl ='{0}' WHERE SQL_Stats_ID = '{1}'".format(anzahl_gesamt_item,sql_stats_id))
                cursor.execute("""UPDATE user SET Aktuell_anz ='{0}', Aktuell_kst = '{1}', Jahr_anz = '{2}', Jahr_kst = '{3}', Total_anz = '{4}', Total_kst = '{5}' 
                WHERE SQL_User_ID = '{6}'""".format(aktuell_anz_user+anzahl, aktuell_kst_user+akt_kst, jahr_anz_user+anzahl, jahr_kst_user+akt_kst, total_anz_user+anzahl, total_kst_user+akt_kst, user_id))
                cnx.commit()
            except:
                cnx.rollback()

        for item_i in items_dict:
            items_dict[item_i].counter.set(0)
        del preis_list[:]
        gesamt_preis_text.set("Buchen: " + str(float(sum(preis_list))) + Euro)
        gui.tk.destroy()
            

    #Abbrechen
    frame_ch_button_abbrechen = Frame(frame_choice, borderwidth = 1, relief = "ridge", height = height_ch_f_button, width = width_ch_f_button)
    choice_button_abbrechen = Button(frame_ch_button_abbrechen, relief = 'ridge', text = "Abbrechen", font = "Arial 14 bold", command = abbrechen, compound = 'center')
    choice_button_abbrechen.config(image = button_bg, width = width_ch_button, height = height_ch_button)
    frame_ch_button_abbrechen.grid_propagate(0)
    choice_button_abbrechen.grid_propagate(0)
    frame_ch_button_abbrechen.grid(column = 0, row = 0, padx = 1, pady = 1)
    choice_button_abbrechen.grid()

    #Reset
    frame_ch_button_reset = Frame(frame_choice, borderwidth = 1, relief = "ridge", height = height_ch_f_button, width = width_ch_f_button)
    choice_button_reset = Button(frame_ch_button_reset, relief = 'ridge', text = "Reset", font = "Arial 14 bold", command = reset, compound = 'center')
    choice_button_reset.config(image = button_bg, width = width_ch_button, height = height_ch_button)
    frame_ch_button_reset.grid_propagate(0)
    choice_button_reset.grid_propagate(0)
    frame_ch_button_reset.grid(column = 1, row = 0, padx = 1, pady = 1)
    choice_button_reset.grid()
    
    #Buchen
    preis_list = []
    gesamt_preis_text = StringVar()
    gesamt_preis_text.set("Buchen: " + str(float(sum(preis_list))) + Euro)
    frame_ch_button_buchen = Frame(frame_choice, borderwidth = 1, relief = "ridge", height = height_ch_f_button, width = width_ch_f_button)
    choice_button_buchen = Button(frame_ch_button_buchen, relief = 'ridge', textvariable = gesamt_preis_text, font = "Arial 14 bold", command = buchen, compound = 'center')
    choice_button_buchen.config(image = button_bg, width = width_ch_button, height = height_ch_button)
    frame_ch_button_buchen.grid_propagate(0)
    choice_button_buchen.grid_propagate(0)
    frame_ch_button_buchen.grid(column = 2, row = 0, padx = 1, pady = 1)
    choice_button_buchen.grid()

    #STATISTIK-FENSTER frame2
    #Anzeige
    name_label = Label(frame2, text = name, font = "Arial 16 bold", wraplength = frame2.winfo_width()-15, justify = "left")
    name_label.grid_propagate(0)
    name_label.grid(column = 0, row = 0, columnspan = 3, padx = 1, pady = 2, sticky = "w")

    zu_zahlen_label1 = Label(frame2, text = "Zu zahlen: ", font = "Arial 12 bold")
    zu_zahlen_label1.grid_propagate(0)
    zu_zahlen_label1.grid(column = 0, row = 1, columnspan = 2, padx = 1, pady = 1, sticky ="w")

    zu_zahlen_label2 = Label(frame2, text = str(zu_zahlen_betrag) + Euro, font = "Arial 12", wraplength = frame2.winfo_width()-10, justify = "left")
    zu_zahlen_label2.grid_propagate(0)
    zu_zahlen_label2.grid(column = 2, row = 2, padx = 1, pady = 1, sticky = "w")

    aufteilung_betrag_label = Label(frame2, text = "Davon: ", font = "Arial 12 bold")
    aufteilung_betrag_label.grid_propagate(0)
    aufteilung_betrag_label.grid(column = 0, row = 3, columnspan = 2, padx = 1, sticky = "w")
    
    betrag_aktuell_label = Label(frame2, text = "Aktueller Monat: " +  str(aktuell_kst) + Euro, font = "Arial 12", wraplength = frame2.winfo_width(), justify = "right")
    betrag_aktuell_label.grid_propagate(0)
    betrag_aktuell_label.grid(column = 1, row = 4, columnspan = 2, padx = 1, sticky = "w")

    uebertrag_label =  Label(frame2, text = "Übertrag: " +  str(uebertrag) + Euro, font = "Arial 12", wraplength = frame2.winfo_width()-aufteilung_betrag_label.winfo_width()-10, justify = "right")
    uebertrag_label.grid_propagate(0)
    uebertrag_label.grid(column = 1, row = 5, columnspan = 2, padx = 1, pady = 5, sticky = "w")

    diesen_monat_label = Label(frame2, text = "Diesen Monat:", font = "Arial 12 bold")
    diesen_monat_label.grid_propagate(0)
    diesen_monat_label.grid(column = 0, row = 6, columnspan = 2, padx = 1, pady = 5, sticky = "w")

    #Tabelle erstellen
    stats_table = SimpleTable(frame2)
    stats_table.grid(column = 1, row = 7, columnspan = 2, padx = 1, pady = 5, sticky = "w")
    #Zähler initialisieren
    row_i = 0
    #Top-4-Liste Anzahl und Getränk suchen mit set aus SimpleTable
    for stat in user_stats[:4]:
        stats_table.set(row_i,0,str(stat[3])+"x")
        item_id = stat[2]
        for item_i in items_list:
            if item_i[0] == item_id:
                stats_table.set(row_i,1,item_i[1])
        row_i += 1

    dieses_jahr_label = Label(frame2, text = "Dieses Jahr:", font = "Arial 12 bold")
    dieses_jahr_label.grid_propagate(0)
    dieses_jahr_label.grid(column = 0, row = 8, columnspan = 2, padx = 1, pady = 5, sticky = "w")

    dieses_jahr_label2 = Label(frame2, text = str(jahr_anzahl) + " Item(s)", font = "Arial, 12")
    dieses_jahr_label2.grid_propagate(0)
    dieses_jahr_label2.grid(column = 1, row = 9, columnspan = 2, padx = 1, sticky = "w")

    total_label = Label(frame2, text = "Total:", font = "Arial 12 bold")
    total_label.grid_propagate(0)
    total_label.grid(column = 0, row = 10, columnspan = 2, padx = 1, pady = 5, sticky = "w")

    total_label2 = Label(frame2, text = str(total_anzahl) + " Item(s)", font = "Arial 12")
    total_label2.grid_propagate(0)
    total_label2.grid(column = 1, row = 11, columnspan = 2, padx = 1, sticky = "w")

    kuchen_label = Label(frame2, text = "Kuchen:", font = "Arial 12 bold")
    kuchen_label.grid_propagate(0)
    kuchen_label.grid(column = 0, row = 12, columnspan = 2, padx = 1, pady = 5, sticky = "w")

    kuchen_label2 = Label(frame2, text = str(kuchen), fg = kuchen_color, font = kuchen_font)
    kuchen_label2.grid_propagate(0)
    kuchen_label2.grid(column = 1, row = 13, columnspan = 2, padx = 1, sticky = "w")

    gui.tk.mainloop()

