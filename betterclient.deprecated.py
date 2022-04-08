import tkinter as tk
import json
import time
import uuid

import datetime


class myframe(tk.Frame):
    def __init__(self, parent, prevframe=None):
        super().__init__(parent)
        self.parent = parent
        self.prevframe = prevframe
        # self.nextframe = nextframe

    # def getnextframe(self):
    #     return self.nextframe
    def backbutton(self):
        if self.prevframe:
            tk.Button(self, text='חזור', fg="black", bg="grey",
                      command=self.goback).grid()

    def getprevframe(self):
        return self.prevframe

    def goback(self):
        if self.prevframe:
            self.pack_forget()
            self.prevframe.pack()


class faultshower(myframe):
    def __init__(self, parent, openfault, c):
        super().__init__(parent)
        # variable storing time
        self.openfault = openfault
        # label displaying time
        self.deletebutton = tk.Button(self, text='X', command=self.ondeletebutton, fg='red', bg='grey')
        self.deletebutton.grid(row=c, column=0)
        self.summarybutton = tk.Button(self, text=self.openfault.getsummary(), command=self.onsummarybutton)
        self.summarybutton.grid(row=c, column=1)
        self.uptimelabel = tk.Label(self, text=self.openfault.getuptime(), bg='grey')
        self.uptimelabel.grid(row=c, column=2)
        # start the timer
        self.uptimelabel.after(100, self.refresh_label)

    def ondeletebutton(self):
        # temporary changes!
        self.grid_forget()
        self.openfault.deletefromlocal()

    def onsummarybutton(self):
        self.parent.pack_forget()
        closefaultframe(self.parent.parent, self.openfault, self.parent).pack()

    def refresh_label(self):
        """ refresh the content of the label every second """
        # display the new time
        self.uptimelabel.configure(text=self.openfault.getuptime())
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.uptimelabel.after(1000, self.refresh_label)


class closefaultframe(myframe):
    def __init__(self, parent, openfault, prevframe=None):
        super().__init__(parent, prevframe)
        self.openfault = openfault
        tk.Label(self, text=self.openfault.getexpandedsummary()).grid()
        for c,field in enumerate(openfault.getfields().items()):
            print(field)
            tk.Label(self,text=field[0]).grid(row=c+1,column=1)
            t = tk.Entry(self,justify='right')
            t.insert(0,field[1])
            if field[1] == "אחר":
                t.configure(fg='red')
            t.grid(row=c+1,column=0)
        self.entry = tk.Entry(self,justify='right')
        self.entry.grid()
        tk.Button(self, text='סגור תקלה', bg='grey', fg='red', command=self.onbuttonclose).grid()
        self.backbutton()

    def onbuttonclose(self):
        self.openfault.closeandsubmit(self.entry.get())
        self.pack_forget()
        openingframe(root).pack()


class openfaultsobject():
    def __init__(self, tid, devicename, devicetype, component, description, starttime=time.time()):
        self.tid = tid
        self.devicename = devicename
        self.devicetype = devicetype
        self.component = component
        self.description = description
        self.starttime = starttime
        # self.open = True

    def getuptime(self):
        # print(time.strftime('%D', time.localtime(time.time() - self.starttime)), time.time() - self.starttime)
        # return time.strftime('%H:%M:%S', time.gmtime(time.time() - self.starttime))
        return str(datetime.timedelta(seconds=time.time() - self.starttime)).split(".")[0]

    def getsummary(self):
        return ' '.join([self.devicename, self.component])

    def getexpandedsummary(self):
        return ' '.join([self.devicename, self.component, self.description])

    def deletefromlocal(self):
        with open('localjson', "r", encoding='utf-8') as file:
            data = json.load(file)
        with open('localjson', "w", encoding='utf-8') as file:
            json.dump(list(filter(lambda i: i["tid"] != self.tid, data)), file, ensure_ascii=False, indent=4)

    def closeandsubmit(self, techcomment):
        entry = {
            "tid": self.tid,
            "description": self.description,
            "component": self.component,
            "devicename": self.devicename,
            "devicetype": self.devicetype,
            # "timetillfixed": (time.time() - self.starttime)/86400, # for excel compatibility
            "timetillfixed": time.time() - self.starttime,
            "techniciancomment": techcomment
        }
        with open('localcompletedfaults.json', "r", encoding='utf-8') as file:
            data = json.load(file)
        # 2. Update json object
        data.append(entry)
        # 3. Write json file
        with open('localcompletedfaults.json', "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.deletefromlocal()
        
    def getfields(self):
        return {'שם אמצעי':self.devicename,'סוג אמצעי':self.devicetype,'רכיב':self.component,'תקלה':self.description}


class openingframe(myframe):
    def __init__(self, parent, prevframe=None):
        super().__init__(parent, prevframe)
        with open('localjson', encoding='utf-8') as f:
            self.openfaults = []
            for i in json.load(f):
                self.openfaults.append(openfaultsobject(**i))
        tk.Button(self, text='פתח תקלה', fg="white", bg="green",
                  command=self.onopenfault).grid(row=0, column=0)
        for c, i in enumerate(self.openfaults):
            faultshower(self, i, c + 1).grid()

    def onopenfault(self):
        self.pack_forget()
        openfaultframedevice(self.parent, self).pack()
    


class openfaultframedevice(myframe):
    def __init__(self, parent, prevframe=None):
        super().__init__(parent, prevframe)
        for dev in config["localdevices"].keys():
            # tk.Button(self, text=dev, foreground="black", background="white",
            #           command=self.goback).grid()
            devicebutton(dev, config["localdevices"][dev], master=self, text=dev, fg="black",
                         bg="white").grid(),
        self.backbutton()


class devicebutton(tk.Button):
    def __init__(self, devicename, devicetype, **kw):
        super().__init__(**kw)
        self.devicename = devicename
        self.devicetype = devicetype
        self.configure(command=self.ontempbutton)

    def ontempbutton(self):
        self.master.pack_forget()
        openfaultframecomponent(self.master.parent, self.devicename, self.devicetype,
                                config["devices"][self.devicetype].keys(), self.master).pack()


class openfaultframecomponent(myframe):
    def __init__(self, parent, devicename, devicetype, components, prevframe=None):
        self.parent = parent
        self.components = components
        self.devicetype = devicetype
        self.devicename = devicename
        super().__init__(parent, prevframe)
        for comp in components:
            componentbutton(comp, self.devicename, self.devicetype, master=self, text=comp, foreground="black",
                            background="white").grid()
        componentbutton("אחר", self.devicename, self.devicetype, master=self, text="אחר", foreground="black",
                        background="white").grid()
        self.backbutton()


class componentbutton(tk.Button):
    def __init__(self, component, devicename, devicetype, **kw):
        super().__init__(**kw)
        self.devicetype = devicetype
        self.devicename = devicename
        self.component = component
        self.configure(command=self.ontempbutton)

    def ontempbutton(self):
        self.master.pack_forget()
        openfaultframedesc(self.master.parent, self.component, self.devicename, self.devicetype,
                           config["devices"][self.devicetype][self.component], self.master).pack()


class openfaultframedesc(myframe):
    def __init__(self, parent, component, devicename, devicetype, descriptions, prevframe=None):
        self.parent = parent
        self.component = component
        self.devicetype = devicetype
        self.devicename = devicename
        super().__init__(parent, prevframe)
        for desc in descriptions:
            submitbutton(desc, self.component, self.devicename, self.devicetype, master=self, text=desc,
                         foreground="black", background="white").grid()
        submitbutton("אחר", self.component, self.devicename, self.devicetype, master=self, text="אחר",
                     foreground="black", background="white").grid()
        self.backbutton()


class submitbutton(tk.Button):
    def __init__(self, description, component, devicename, devicetype, **kw):
        super().__init__(**kw)
        self.description = description
        self.component = component
        self.devicename = devicename
        self.devicetype = devicetype
        self.configure(command=self.ontempbutton)

    def ontempbutton(self):
        entry = {
            "tid": str(uuid.uuid4()),
            "description": self.description,
            "component": self.component,
            "devicename": self.devicename,
            "devicetype": self.devicetype,
            "starttime": time.time()
        }
        with open('localjson', "r", encoding='utf-8') as file:
            data = json.load(file)
        # 2. Update json object
        data.append(entry)
        # 3. Write json file
        with open('localjson', "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.master.pack_forget()
        openingframe(root).pack()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('מערכת תיעוד תקלות')
    root.geometry('300x400')
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    tk.Label(root, text=config['user']).pack()
    openingframe(root).pack()
    # openframe = tkinter.Frame(root)
    # openframe.pack()
    # with open('config.json', encoding='utf-8') as f:
    #     config = json.load(f)
    # tk.Label(openframe, text=f'שלום {config["user"]}').grid(row=0, column=1)
    # butt = tk.Button(openframe, text='פתח תקלה', foreground="black", background="white", command=opentakala_button)
    # butt.grid(row=0, column=0)
    # openedtakalot = []
    # with open('localjson', encoding='utf-8') as f:
    #     temp = json.load(f)
    #     for i in temp:
    #         openedtakalot.append(opentakala(**i))
    # for c, i in enumerate(openedtakalot):
    #     upTimer(openframe,i,c+1)

    # tk.Label(text=f'שלום {user}').grid(row=0,column=0,sticky='ne')
    # for r,i in enumerate(js.keys()):
    #     tk.Label(text=i).grid(row=r,column=0)
    #     for c,j in enumerate(js[i].keys()):
    #         tk.Label(text=j).grid(row=r,column=c+1)
    root.mainloop()
