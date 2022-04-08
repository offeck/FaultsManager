import tkinter
import tkinter as tk
import json
import time
import uuid

class upTimer:
    def __init__(self, parent, takala,c):
        # variable storing time
        self.takala = takala
        self.uptime = takala.getuptime()
        self.tid = takala.tid
        self.parent= parent
        # label displaying time
        self.summarybutton = tk.Button(parent, text=i.getsummary(), command=self.summarybuttonpressed)
        self.summarybutton.grid(row=c, column=0)
        self.uptimelabel = tk.Label(parent, text=self.uptime)
        self.uptimelabel.grid(row=c,column=1)
        # start the timer
        self.uptimelabel.after(100, self.refresh_label)
    def summarybuttonpressed(self):
        closetakala(self.takala)
    def refresh_label(self):
        """ refresh the content of the label every second """
        # increment the time
        self.uptime = self.takala.getuptime()
        # display the new time
        self.uptimelabel.configure(text=self.uptime)
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.uptimelabel.after(1000, self.refresh_label)


class opentakala():
    def __init__(self, tid,devicename, devicetype, component, description, starttime=time.time()):
        self.tid = tid
        self.devicename=devicename
        self.devicetype = devicetype
        self.component = component
        self.description = description
        self.starttime = str(starttime)

    def getuptime(self):
        return time.strftime('%H:%M:%S', time.gmtime(time.time() - float(self.starttime)))

    def getsummary(self):
        return ' '.join([self.devicename, self.component])


js = {
    'בלון': {
        'תקשורת': "מסך שחור",
        'מצלמת יום': "מסך דהוי",
        'מצלמה תרמית': "מצלמה לא מתכיילת",
    }
}
def goback():
    pass

def opentakala_button():
    openframe.pack_forget()
    opentakalaframe = tkinter.Frame(window)
    opentakalaframe.pack()
    for i in config["localdevices"].keys():
        tk.Label(opentakalaframe,text=i).grid()
    tk.Button(opentakalaframe,text="חזור",command=goback).grid()

def closetakala(takala):
    openframe.pack_forget()
    closetakalaframe = tkinter.Frame(window)
    closetakalaframe.pack()
    print(takala)
    upTimer(closetakalaframe,takala,0)
    # tk.Label(closetakalaframe,text=takala.getsummary()).grid(column=1,row=0)
    tk.Label(closetakalaframe, text="פתרון תקלה").grid(column=1, row=1)
    tk.Entry(closetakalaframe).grid(column=0, row=1)
    tk.Button(closetakalaframe,text="סגור תקלה",command=reporttakala).grid(columnspan=2,column=0,row=2)

def reporttakala():
    pass

if __name__ == '__main__':
    window = tk.Tk()
    openframe = tkinter.Frame(window)
    openframe.pack()
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    tk.Label(openframe, text=f'שלום {config["user"]}').grid(row=0, column=1)
    butt = tk.Button(openframe, text='פתח תקלה', foreground="black", background="white", command=opentakala_button)
    butt.grid(row=0, column=0)
    openedtakalot = []
    with open('localjson', encoding='utf-8') as f:
        temp = json.load(f)
        for i in temp:
            openedtakalot.append(opentakala(**i))
    for c, i in enumerate(openedtakalot):
        upTimer(openframe,i,c+1)

    # tk.Label(text=f'שלום {user}').grid(row=0,column=0,sticky='ne')
    # for r,i in enumerate(js.keys()):
    #     tk.Label(text=i).grid(row=r,column=0)
    #     for c,j in enumerate(js[i].keys()):
    #         tk.Label(text=j).grid(row=r,column=c+1)
    window.mainloop()
