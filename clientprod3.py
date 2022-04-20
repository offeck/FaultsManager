from ast import arg
import tkinter as tk
import json
import time
import uuid
from functools import partial
import datetime


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]




class myframe(tk.Frame):
    def __init__(self, *, parent: tk.Frame, openfaults: list = None, prevframe: tk.Frame = None):
        super().__init__(parent, bg='#222831')
        self.parent = parent
        self.prevframe = prevframe
        self.openfaults = openfaults
        # self.nextframe = nextframe

    # def getnextframe(self):
    #     return self.nextframe
    def backbutton(self, **kw):
        if self.prevframe:
            self.bt = mybutton('#AAAAAA', self, text='חזור', fg="#00ADB5", bg="#DDDDDD",
                               command=self.goback, **regfont)
            self.bt.grid(**kw)

    def getprevframe(self):
        return self.prevframe

    def goback(self):
        if self.prevframe:
            self.pack_forget()
            self.prevframe.pack()


class mybutton(tk.Button):
    def __init__(self, coloronhover, *args, **kw):
        super().__init__(*args, **kw)
        self.coloronleave = self['bg']
        self.coloronhover = coloronhover

        self.bind("<Enter>", func=lambda e: self.config(
            bg=self.coloronhover))

        # background color on leving widget
        self.bind("<Leave>", func=lambda e: self.config(
            bg=self.coloronleave))


class faultshower(myframe):
    def __init__(self, parent, openfault, c):
        super().__init__(parent=parent)
        # variable storing time
        self.openfault = openfault
        # label displaying time
        self.deletebutton = mybutton('#15191f',
                                     self, text='X', command=self.ondeletebutton, **regfont, fg='#ab0317', bg='#222831')
        self.deletebutton.grid(row=c, column=0)
        self.summarybutton = mybutton('#15191f', self, text=self.openfault.getsummary(
        ), command=self.onsummarybutton, bg='#222831', **regfont, fg='#EEEEEE')
        self.summarybutton.grid(row=c, column=1)
        self.uptimelabel = tk.Label(
            self, text=self.openfault.getuptime(), **regfont, bg='#008187', fg='#EEEEEE')
        self.uptimelabel.grid(row=c, column=2)
        # start the timer
        self.uptimelabel.after(100, self.refresh_label)

    def ondeletebutton(self):
        # temporary changes!
        # self.grid_forget()
        self.destroy()
        self.openfault.deletefromlocal()
        self.parent.openfaults.remove(self.openfault)

    def onsummarybutton(self):
        # self.grid_forget()
        self.parent.pack_forget()
        closefaultframe(self.parent.parent, self.parent.openfaults,
                        self.openfault, self.parent).pack()

    def refresh_label(self):
        """ refresh the content of the label every second """
        # display the new time
        try:
            self.uptimelabel.configure(text=self.openfault.getuptime())
            # request tkinter to call self.refresh after 1s (the delay is given in ms)
            self.uptimelabel.after(1000, self.refresh_label)
        except (TypeError, ValueError) as e:
            print(type(e), 'starttimeerror')


class closefaultframe(myframe):
    def __init__(self, parent, openfaults, openfault, prevframe):
        super().__init__(parent=parent, openfaults=openfaults, prevframe=prevframe)
        self.openfault = openfault
        tk.Label(self, text=self.openfault.getexpandedsummary(),
                 fg="#DDDDDD", bg="#00ADB5", **regfont).grid(columnspan=2, pady=10)
        self.entries = []
        # self.translated = True
        for c, field in enumerate(openfault.getfields(['devicename', 'component', 'description', 'techcomment'], True).items()):
            print(field)
            tk.Label(self, text=field[0], bg='#393E46',
                     fg='#00ADB5', **regfont).grid(row=c+1, column=1, sticky='ew')
            print(get_keys_from_value(engtohebdict, field[0]))
            self.entries.append((get_keys_from_value(engtohebdict, field[0])[
                                0], tk.Entry(self, justify='right', **regfont, bg='#DDDDDD')))
            self.entries[-1][1].insert(0, field[1])
            if field[1] == "אחר":
                self.entries[-1][1].configure(fg='red')
            self.entries[-1][1].grid(row=c+1, column=0, pady=(0, 7))
        self.closebutton = mybutton('#222831', self, text='סגור תקלה', fg="#00ADB5", bg="#393E46", **regfont,
                                    command=self.onbuttonclose)
        self.closebutton.grid(columnspan=2, pady=(0, 7))
        self.backbutton(columnspan=2)

    def onbuttonclose(self):
        self.openfault.closeandsubmit({i[0]: i[1].get() for i in self.entries})
        self.pack_forget()
        self.openfaults.remove(self.openfault)
        openingframe(root, self.openfaults).pack()


class openfaultobject(dict):
    data: dict

    def __init__(self, data):
        super().__init__(data)
        if 'techcomment' not in self:  # temporary solution
            self.update({'techcomment': ''})  # temporary solution
        # self.open = True

    def getuptime(self):
        # print(time.strftime('%D', time.localtime(time.time() - self.starttime)), time.time() - self.starttime)
        # return time.strftime('%H:%M:%S', time.localtime(time.time() - self.starttime))
        return str(datetime.timedelta(seconds=time.time() - self['starttime'])).split(".")[0]
        # return time.strftime('%H:%M:%S',time.gmtime(time.time()-self['starttime']))

    def getsummary(self):
        return ' '.join([self['devicename'], self['component']])

    def getexpandedsummary(self):
        return ' '.join([self['devicename'], self['component'], self['description']])

    def deletefromlocal(self):
        with open(localjsonpath, "r", encoding='utf-8') as file:
            data = json.load(file)
        with open(localjsonpath, "w", encoding='utf-8') as file:
            print(self['tid'])
            json.dump(list(filter(
                lambda i: i["tid"] != self['tid'], data)), file, ensure_ascii=False, indent=4)
        # openfaults.remove(self)

    def closeandsubmit(self, data):
        self.update({'timetillfixed': time.time() - self['starttime']})
        self.update(data)
        # self.pop('starttime', None) temporary change to check excel compatibility
        self['starttime'] = time.strftime(
            '%d/%m/%Y %H:%M:%S', time.localtime(time.time()))
        with open(completedjsonpath, "r", encoding='utf-8') as file:
            filedata = json.load(file)
        # 2. Update json object
        filedata.append(self)
        # 3. Write json file
        with open(completedjsonpath, "w", encoding='utf-8') as file:
            json.dump(filedata, file, ensure_ascii=False, indent=4)
        self.deletefromlocal()

    def getfields(self, keys=None, translated=False):
        # print(set(keys).issubset(self.keys()), keys, list(self.keys()))
        # data = OrderedDict()
        data = {i: self[i] for i in keys} if keys and set(
            keys).issubset(self.keys()) else self
        print(data)
        if translated:
            # sharedkeys = set(data.keys()).intersection(engtohebdict.keys())
            sharedkeys = [
                key for key in data.keys() if key in engtohebdict.keys()]
            print(sharedkeys)
            for key in sharedkeys:
                data.update({engtohebdict[key]: self[key]})
                data.pop(key, None)
            return data
        return data


class openingframe(myframe):
    def __init__(self, parent, openfaults):
        super().__init__(parent=parent, openfaults=openfaults)
        self.openfaultbutton = mybutton('#008187', self, text='פתח תקלה', fg="#EEEEEE", **regfont, bg="#00ADB5",
                                        command=self.onopenfault)
        self.openfaultbutton.grid(row=0, column=0, pady=(0, 10))
        for c, i in enumerate(self.openfaults):
            faultshower(self, i, c + 1).grid(pady=(0, 7))

    def onopenfault(self):
        self.pack_forget()
        openfaultframe(stages[0], config['localdevices'],
                       self.parent, self.openfaults, self).pack()


class openfaultframe(myframe):  # stages need changes
    def __init__(self, stage, options, parent, openfaults, prevframe, data={}):
        super().__init__(parent=parent, openfaults=openfaults, prevframe=prevframe)
        # print(f'options : {options}')
        self.options = options
        self.stage = stage
        self.data = data
        self.islast = self.stage==stages[-1]
        collength = 3
        tk.Label(master=self, text=engtohebdict[stage], fg="#DDDDDD",
                 bg="#00ADB5", **regfont).grid(pady=10, columnspan=collength)
        iterable = self.options if self.islast else list(self.options.keys())
        new_list = [iterable[i:i+collength]
                    for i in range(0, len(iterable), collength)]
        for row, tup in enumerate(new_list, 1):
            x = myframe(parent=self)
            [mybutton('#222831', x, text=opt, **regfont, fg="#00ADB5",
                      bg="#393E46", command=partial(self.onbuttonpress, opt)).grid(pady=(0, 7), row=0, column=col) for col, opt in enumerate(sorted(tup, reverse=True))]
            x.grid(row=row)
        self.backbutton(columnspan=collength)

    def onbuttonpress(self, opt):
        self.pack_forget()
        self.data.update({self.stage: opt, 'devicetype': self.options[opt]}if self.stage == stages[0] else {
                         self.stage: opt})
        # print(self.data,)
        if self.islast:
            print(f'self.data : {self.data}')
            # print(all((any((i[stage]!=self.data[stage] for stage in stages)) for i in self.openfaults)),self.openfaults)
            if all((any((i[stage] != self.data[stage] for stage in stages)) for i in self.openfaults)):
                self.data.update(
                    {"tid": str(uuid.uuid4()), "starttime": time.time()})
                with open(localjsonpath, "r", encoding='utf-8') as file:
                    data = json.load(file)
                data.append(self.data)
                with open(localjsonpath, "w", encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                self.openfaults.append(openfaultobject(self.data))
                openingframe(self.master, self.openfaults).pack()
                return
            self.data.pop(self.stage, None)
            self.pack()
            tk.Label(master=self, **regfont, text='תקלה פתוחה זאת קיימת',
                     fg='red', bg=self['bg']).grid()
            return
        options = config["devices"][self.options[opt]
                                    ] if self.stage == stages[0] else self.options[opt]
        openfaultframe(stages[stages.index(self.stage)+1],
                       options, self.master, self.openfaults, self).pack()


if __name__ == '__main__':
    with open('D:\Projects\Python\FaultsManager\config.json', encoding='utf-8') as f:
        config = json.load(f)
    localjsonpath = config['localjson']
    stages = ['devicename', 'component', 'description']
    completedjsonpath = config['completedjson']
    engtohebdict = config['engtohebdict']
    root = tk.Tk()
    root.title('תיעוד תקלות')
    regfont = {'font': (
        "calibri", 18)}
    # root.geometry('300x400')
    root.configure(bg='#222831')
    tk.Label(root, text=config['user'], font=(
        "calibri", 20), bg='#222831', fg='#00ADB5').pack(padx=100)
    with open(localjsonpath, encoding='utf-8') as f:
        openingframe(root, [openfaultobject(i)
                     for i in json.load(f)]).pack(pady=(15, 0))
    root.mainloop()
