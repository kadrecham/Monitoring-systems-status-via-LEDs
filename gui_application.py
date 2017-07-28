from Tkinter import *
import tkMessageBox
import sys
import os
import time
import sqlite3
from threading import Thread

class Application (Frame):

    def __init__(self, master):
        Frame.__init__(self,master)
        self.rFlag = 0
        self.grid()
        self.conn = self.connectdb('config')
        self.create_widgets()
        self.initialize()
        self.colorIndex = {'Red':'0,255,0', 'Orange':'120,255,0', 'Yellow':'255,255,0', 'Green':'255,0,0', 'Blue':'0,0,255', 'Violet':'0,128,128', 'White':'127,127,127', 'Off':'0,0,0'}

    def connectdb(self, db):
        try:
            conn = sqlite3.connect(db)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(e)
            sys.exit()

    def initialize(self):
        try:
            c = self.conn.cursor()
            if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leds'").fetchall() and c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quit'").fetchall():
                print "Initializing..."
                self.stop_LEDs()
            else:
                print "Creating database...."
                c.execute ("CREATE TABLE IF NOT EXISTS leds (ledNumber int, up_color text, down_color text, blink int, source text, proxy int, host text, port int, sourceID text, dbName text, user text, password text, dbQuery text)") 
                c.execute ("CREATE TABLE IF NOT EXISTS quit (qFlag int)")
                c.execute ("INSERT INTO quit VALUES (1)")
                for i in range (60):
                    c.execute ("INSERT INTO leds VALUES (?,'0,0,0','0,0,0',0,'',0,'','','','','','','')", (i,)) 
                print "Initializing..."
                self.stop_LEDs()
        except Exception as e:
            print (e)
            sys.exit()

    def delete_data(self):
        if self.ledNumber.get() == '':
            tkMessageBox.showwarning("Warning!", "Please select the LED number!")
        else:
            if tkMessageBox.askyesno("Warning!", "Do you want reset the LED" + self.ledNumber.get()):
                try:
                    c = self.conn.cursor()
                    result = c.execute ("SELECT * FROM leds WHERE ledNumber=?", (self.ledNumber.get(),)).fetchall()
                    if len(result) == 0:
                        print "Reset LED number", self.ledNumber.get(), "..."
                        c.execute ("INSERT INTO leds VALUES (?,'0,0,0','0,0,0',0,'',0,'','','','','','','')", (self.ledNumber.get()))
                        self.conn.commit()
                        print "Done!"
                    else:
                        print "Reset LED number", self.ledNumber.get(), "..."
                        c.execute ("UPDATE leds SET up_color='0,0,0', down_color='0,0,0', blink=0, source='', proxy=0, host='', port='', sourceID='', dbName='', user='', password='', dbQuery='' WHERE ledNumber=?", (self.ledNumber.get(),))
                        self.conn.commit()
                        print "Done!"
                except Exception as e:
                    print ("Save failed. {}".format(e))

    def save_data(self):  
        if self.ledNumber.get() == '' or self.color1.get() == ''or self.color1.get()== '' or self.dataSource.get() == '':
            tkMessageBox.showwarning("Warning!", "Please select the LED number, UP state color, DOWN state color, DOWN state and Datasource...!")
        else:
            if self.color1.get() != 'Off' and self.color1.get() == self.color2.get():
                tkMessageBox.showwarning("Warning!", "UP color and DOWN color should be different..!")
            else:
                if self.dataSource.get() == 'Server' and self.hostName.get() == '':
                    tkMessageBox.showwarning("Warning!", "Please enter Host name!")
                else:
                    if self.dataSource.get() == 'InfluxDB' and (self.hostName.get()=='' or self.portNumber.get() == '' or self.dbName.get()=='' or  self.userName.get()=='' or self.password.get()=='' or self.query.get()==''):
                        tkMessageBox.showwarning("Warning!", "Please enter host name, port number, database name, user, password and query!")
                    else:
                        if self.dataSource.get() == 'Grafana' and (self.hostName.get()=='' or self.portNumber.get() == '' or self.sourceID.get()=='' or self.dbName.get()=='' or  self.userName.get()=='' or self.password.get()=='' or self.query.get()==''):
                            tkMessageBox.showwarning("Warning!", "Please enter host name, port number, sourceID, database name, user, password and query!")
                        else:
                            try:
                                c = self.conn.cursor()
                                result = c.execute ("SELECT * FROM leds WHERE ledNumber=?", (self.ledNumber.get(),)).fetchall()
                                if len(result) == 0:
                                    print "Setting LED number", self.ledNumber.get(), "..."
                                    c.execute ("INSERT INTO leds VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (self.ledNumber.get(), self.colorIndex[self.color1.get()], self.colorIndex[self.color2.get()], self.blink.get(), self.dataSource.get(), self.prox.get(), self.hostName.get(), self.portNumber.get(), self.sourceID.get(), self.dbName.get(), self.userName.get(), self.password.get(), self.query.get()))
                                    self.conn.commit()
                                    print "Done!"
                                else:
                                    print "Setting LED number", self.ledNumber.get(), "..."
                                    c.execute ("UPDATE leds SET up_color=?, down_color=?, blink=?, source=?, proxy=?, host=?, port=?, sourceID=?, dbName=?, user=?, password=?, dbQuery=? WHERE ledNumber=?", (self.colorIndex[self.color1.get()], self.colorIndex[self.color2.get()], self.blink.get(), self.dataSource.get(), self.prox.get(), self.hostName.get(), self.portNumber.get(), self.sourceID.get(), self.dbName.get(), self.userName.get(), self.password.get(), self.query.get(),self.ledNumber.get()))
                                    self.conn.commit()
                                    print "Done!"
                            except Exception as e:
                                print ("Save failed. {}".format(e))
            
    def run_LEDs_thread(self):
            try:
                print 'Running... \nPlease wait... '
                c = self.conn.cursor()
                c.execute ("UPDATE quit SET qFlag=? WHERE ROWID=?", (0,1))
                self.conn.commit()
                time.sleep(2)
                self.stopButton.config(state="normal")
                self.startButton.config(state=DISABLED)
                self.thread = Thread(target=self.run_LEDs)
                self.thread.deamon = True
                self.thread.start()
            except Exception as e:
                    print ("Start failed! {}".format(e))
    
    def run_LEDs(self):
        os.system("sudo python leds_driver.py")

    def stop_LEDs(self):
        for x in range (5):
            try:
                print 'Please wait... '
                c = self.conn.cursor()
                c.execute ("UPDATE quit SET qFlag=? WHERE ROWID=?", (1,1))
                self.conn.commit()
                time.sleep(5)
                self.stopButton.config(state=DISABLED)
                self.startButton.config(state="normal")
                print "Done!"
                break
            except Exception as e:
                    print ("Stop failed! {}".format(e))
        
        
            
    def create_widgets(self):
        Label(self, text = "").grid(row = 0, column = 0, sticky = W)
        Label(self, text = "Select the LED number, UP state color, DOWN state color and Datasource: ").grid(row = 1, column = 0, columnspan = 10, sticky = W)
        Label(self, text = "").grid(row = 2, column = 0, sticky = W)

        Label(self, text = "LED number:").grid(row = 3, column = 0, sticky = E)
        self.ledNumber = StringVar()
        self.ledNumber.set ('')
        choices = range(0, 60)
        om1 = OptionMenu(self, self.ledNumber, *choices)
        om1.config(width = 5)
        om1.grid(row = 3, column = 1, sticky = W)

        Label(self, text = "UP color:").grid(row = 3, column = 2, sticky = E)
        self.color1 = StringVar()
        self.color1.set("")
        colorSet = ('Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Violet', 'White', 'Off')
        om2 = OptionMenu(self, self.color1, *colorSet)
        om2.config(width = 5)
        om2.grid(row = 3, column = 3, sticky = W)

        Label(self, text = "DOWN color:").grid(row = 3, column = 4, sticky = E)
        self.color2 = StringVar()
        self.color2.set("")
        om3 = OptionMenu(self, self.color2, *colorSet)
        om3.config(width = 5)
        om3.grid(row = 3, column = 5, sticky = W)
        
        Label(self, text = "Source:").grid(row = 3, column = 6, sticky = E)
        self.dataSource = StringVar()
        self.dataSource.set("")
        dataSourceSet = ['Grafana', 'InfluxDB', 'Server']
        om4 = OptionMenu(self, self.dataSource, *dataSourceSet)
        om4.config(width = 5)
        om4.grid(row = 3, column = 7, sticky = W)

        Label(self, text = "", width = 2).grid(row = 3, column = 8, sticky = E)
        
        self.blink = BooleanVar()
        self.blink.set(False)
        Checkbutton(self, text = "Blinking", variable = self.blink, onvalue=True, offvalue=False ).grid(row = 4, column = 5, sticky = W)

        self.prox = BooleanVar()
        self.prox.set(False)
        Checkbutton(self, text = "Escape proxy", variable = self.prox, onvalue=True, offvalue=False ).grid(row = 4, column = 7, sticky = W)

        Label(self, text = "").grid(row = 5, column = 0, sticky = W)
        Label(self, text = "Enter the host name, the port number and Source ID:").grid(row = 6, column = 0, columnspan = 5, sticky = W)

        Label(self, text = "Host Name:").grid(row = 7, column = 0, sticky = E)
        self.hostName = StringVar()
        Entry(self, textvariable = self.hostName).grid(row = 7, column = 1, columnspan = 2, sticky = W)

        Label(self, text = "Port:").grid(row = 7, column = 3, sticky = E)
        self.portNumber = StringVar()
        Entry(self, textvariable = self.portNumber, width = 5).grid(row = 7, column = 4, sticky = W)

        Label(self, text = "Source ID:").grid(row = 7, column = 5, sticky = E)
        self.sourceID = StringVar()
        Entry(self, textvariable = self.sourceID, width = 5).grid(row = 7, column = 6, sticky = W)

        Label(self, text = "").grid(row = 8, column = 0, sticky = W)
        Label(self, text = "Enter the database name, username and password: ").grid(row = 9, column = 0, columnspan = 5, sticky = W)

        Label(self, text = "Database:").grid(row = 10, column = 0, sticky = E)
        self.dbName = StringVar()
        Entry(self, textvariable = self.dbName).grid(row = 10, column = 1, columnspan = 2, sticky = W)

        Label(self, text = "User:").grid(row = 10, column = 3, sticky = E)
        self.userName = StringVar()
        Entry(self, textvariable = self.userName, width = 10).grid(row = 10, column = 4, sticky = W)

        Label(self, text = "Password:").grid(row = 10, column = 5, sticky = E)
        self.password = StringVar()
        Entry(self, textvariable = self.password, show="*", width = 10).grid(row = 10, column = 6, sticky = W)

        Label(self, text = "").grid(row = 11, column = 0, sticky = W)
        Label(self, text = "Enter the query: ").grid(row = 12, column = 0, sticky = W)

        Label(self, text = "Query:").grid(row = 13, column = 0, sticky = E)
        self.query = StringVar()
        Entry(self, textvariable = self.query, width = 66).grid(row = 13, column = 1, columnspan = 7, sticky = W)
        
        Label(self, text = "").grid(row = 14, column = 0, sticky = W)
        Label(self, text = "").grid(row = 15, column = 0, sticky = W)
        Button(self, text = "Reset", command = self.delete_data).grid(row = 16, column = 2, sticky = W)
        Button(self, text = " Set ", command = self.save_data).grid(row = 16, column = 1, sticky = E)
        self.startButton = Button(self, text = "Start", state="normal", command = self.run_LEDs_thread)
        self.startButton.grid(row = 16, column = 5, sticky = E)
        
        self.stopButton = Button(self, text = "Stop", state="normal", command = self.stop_LEDs)
        self.stopButton.grid(row = 16, column = 6, sticky = W)
            
        Label(self, text = "").grid(row = 17, column = 0, sticky = W)
        Label(self, text = "").grid(row = 18, column = 0, sticky = W)


if __name__ == '__main__':        
    root = Tk()
    root.title("LED Monitoring System")
    app = Application(root)
    root.mainloop()
