import tkinter as tk
import json
import time
import uuid
from functools import partial
import datetime


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]

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
        try:
            self.uptimelabel.configure(text=self.openfault.getuptime())
        except:
            self.grid_forget()
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.uptimelabel.after(1000, self.refresh_label)


class closefaultframe(myframe):
    def __init__(self, parent, openfault, prevframe=None):
        super().__init__(parent, prevframe)
        self.openfault = openfault
        tk.Label(self, text=self.openfault.getexpandedsummary()).grid()
        self.entries = []
        # self.translated = True
        for c,field in enumerate(openfault.getfields(['devicename','component','description','techcomment'],True).items()):
            print(field)
            tk.Label(self,text=field[0]).grid(row=c+1,column=1)
            print(get_keys_from_value(engtoheb,field[0]))
            self.entries.append((get_keys_from_value(engtoheb,field[0])[0],tk.Entry(self,justify='right')))
            self.entries[-1][1].insert(0,field[1])
            if field[1] == "אחר":
                self.entries[-1][1].configure(fg='red')
            self.entries[-1][1].grid(row=c+1,column=0)
        tk.Button(self, text='סגור תקלה', bg='grey', fg='red', command=self.onbuttonclose).grid()
        self.backbutton()

    def onbuttonclose(self):
        self.openfault.closeandsubmit({i[0]:i[1].get() for i in self.entries})
        self.pack_forget()
        openingframe(root).pack()

class openfaultsobject(dict):
    data: dict

    def __init__(self, data):
        super().__init__(data)
        if 'techcomment' not in self: # temporary solution
            self.update({'techcomment':''}) # temporary solution
        # self.open = True

    def getuptime(self):
        # print(time.strftime('%D', time.localtime(time.time() - self.starttime)), time.time() - self.starttime)
        # return time.strftime('%H:%M:%S', time.gmtime(time.time() - self.starttime))
        try:
            return str(datetime.timedelta(seconds=time.time() - self['starttime'])).split(".")[0]
        except:
            return ValueError

    def getsummary(self):
        return ' '.join([self['devicename'], self['component']])

    def getexpandedsummary(self):
        return ' '.join([self['devicename'], self['component'], self['description']])

    def deletefromlocal(self):
        with open(localjson, "r", encoding='utf-8') as file:
            data = json.load(file)
        with open(localjson, "w", encoding='utf-8') as file:
            print(self['tid'])
            json.dump(list(filter(lambda i: i["tid"] != self['tid'], data)), file, ensure_ascii=False, indent=4)

    def closeandsubmit(self, data):
        self.update({'timetillfixed':time.time() - self['starttime']})
        self.update(data)
        self.pop('starttime', None)
        with open(completedjson, "r", encoding='utf-8') as file:
            filedata = json.load(file)
        # 2. Update json object
        filedata.append(self)
        # 3. Write json file
        with open(completedjson, "w", encoding='utf-8') as file:
            json.dump(filedata, file, ensure_ascii=False, indent=4)
        self.deletefromlocal()

    def getfields(self,keys=None,translated=False):
        # print(set(keys).issubset(self.keys()), keys, list(self.keys()))
        data = {i:self[i] for i in keys} if keys and set(keys).issubset(self.keys()) else self
        if translated:
            sharedkeys = set(data.keys()).intersection(engtoheb.keys())
            for key in sharedkeys:
                data.update({engtoheb[key]:self[key]})
                data.pop(key, None)
            return data
        return data


class openingframe(myframe):
    def __init__(self, parent, prevframe=None):
        super().__init__(parent, prevframe)
        tk.Button(self, text='פתח תקלה', fg="white", bg="green",
                  command=self.onopenfault).grid(row=0, column=0)
        self.openfaults = []
        with open(localjson, encoding='utf-8') as f:
            for i in json.load(f):
                self.openfaults.append(openfaultsobject(i))
        for c, i in enumerate(self.openfaults):
            faultshower(self, i, c + 1).grid()
    def cleanopenfaults(self):
        self.openfaults = []
    def onopenfault(self):
        self.pack_forget()
        openfaultframe(stages[0],config['localdevices'],self.parent,self).pack()
        # openfaultframedevice(self.parent, self).pack()
# openfaultframe(config["localdevices"].keys())



class openfaultframe(myframe):
    def __init__(self, stage, options, parent ,prevframe=None, data = {}):
        super().__init__(parent, prevframe)
        # print(f'options : {options}')
        self.options = options
        self.stage = stage
        self.data = data
        tk.Label(master=self,text=engtoheb[stage],fg='grey').grid()
        iterable = self.options if isinstance(self.options,list) else self.options.keys()
        for opt in iterable:
            tk.Button(master=self, text=opt, fg="black",
                         bg="white",command=partial(self.onbuttonpress,opt)).grid()
        self.backbutton()

    def onbuttonpress(self,opt):
        self.pack_forget()
        self.data.update({self.stage:opt,'devicetype':self.options[opt]}if self.stage==stages[0] else {self.stage:opt})
        # print(self.data,)
        if isinstance(self.options,list):
            print(f'self.data : {self.data}')
            self.data.update({"tid": str(uuid.uuid4()),"starttime": time.time()})
            with open(localjson, "r", encoding='utf-8') as file:
                    data = json.load(file)
            data.append(self.data)
            with open(localjson, "w", encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            openingframe(self.master).pack()
            self.data.clear()
            return
        options = config["devices"][self.options[opt]] if self.stage==stages[0] else self.options[opt]
        openfaultframe(stages[stages.index(self.stage)+1],options, self.master,self).pack()


if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    localjson = config['localjson']
    stages = ['devicename','component','description']
    completedjson = config['completedjson']
    engtoheb = {"description": "פירוט תקלה",
                "component": "רכיב תקלה",
                "devicename": "שם אמצעי",
                "devicetype": "סוג אמצעי",
                "timetillfixed":"זמן",
                "starttime":"זמן התחלה",
                "techcomment":"פיתרון תקלה"}
    root = tk.Tk()
    root.title('מערכת תיעוד תקלות')
    root.geometry('300x400')
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
    # with open(localjson, encoding='utf-8') as f:
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