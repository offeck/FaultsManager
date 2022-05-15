import tkinter as tk
import json
import time
import uuid
from functools import partial
import datetime
import os


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


class faultshower():
    def __init__(self, parent, openfault, c):
        # super().__init__(parent=parent)
        # variable storing time
        self.parent = parent
        self.openfault = openfault
        # label displaying time
        self.deletebutton = mybutton('#15191f',
                                     parent, image=deletephoto, command=self.ondeletebutton, **regfont, fg='#ab0317', bg='#222831')
        self.deletebutton.grid(
            row=c, column=0, sticky='ewns', pady=(0, 15), ipadx=5)
        self.summarybutton = mybutton('#15191f', parent, text=self.openfault.getsummary(
        ), command=self.onsummarybutton, bg='#222831', **regfont, fg='#EEEEEE')
        self.summarybutton.grid(
            row=c, column=1, sticky='ewns', pady=(0, 15), padx=10)
        self.uptimelabel = tk.Label(
            parent, text=self.openfault.getuptime(), **regfont, bg='#008187', fg='#EEEEEE')
        self.uptimelabel.grid(row=c, column=2, sticky='ewns', pady=(0, 15))
        # start the timer
        self.uptimelabel.after(100, self.refresh_label)

    def ondeletebutton(self):
        # temporary changes!
        # self.grid_forget()
        # self.destroy()

        self.deletebutton.destroy()
        self.summarybutton.destroy()
        self.uptimelabel.destroy()

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
        # print(openfault.getfields(closestages, True))
        for c, field in enumerate(openfault.getfields(closestages, True).items()):
            tk.Label(self, text=field[0], bg='#393E46',
                     fg='#00ADB5', **regfont).grid(row=c+1, column=1, sticky='ew')
            print('field ', field)
            print('getkeysfromvalue : ', get_keys_from_value(
                engtohebdict, field[0]))
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

    def __init__(self, data: dict):
        super().__init__(**data.copy())
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
        print(set(
            keys), self.keys(), set(keys).issubset(self.keys()))
        data = {i: self[i] for i in keys if i in self} if keys else self
        print(f'data before translation {data}')
        if translated:
            # sharedkeys = set(data.keys()).intersection(engtohebdict.keys())
            sharedkeys = [
                key for key in data.keys() if key in engtohebdict.keys()]
            print(f'shared keys {sharedkeys}')
            for key in sharedkeys:
                data.update({engtohebdict[key]: self[key]})
                data.pop(key, None)
            print(f'translated data returned {data}')
            return data
        return data


class openingframe(myframe):
    def __init__(self, parent, openfaults):
        super().__init__(parent=parent, openfaults=openfaults)
        self.openfaultbutton = mybutton('#008187', self, text='פתח תקלה', fg="#EEEEEE", **regfont, bg="#00ADB5",
                                        command=self.onopenfault)
        self.openfaultbutton.grid(columnspan=3, pady=(0, 15))
        for c, i in enumerate(self.openfaults):
            faultshower(self, i, c + 1)

    def onopenfault(self):
        self.pack_forget()
        print(openstages[0])
        openfaultframe(parent=self.parent, openfaults=self.openfaults, prevframe=self,
                       stage=openstages[0], options=config['localdevices']).pack()


class openfaultframe(myframe):  # stages need changes
    def __init__(self, *, parent, openfaults, prevframe, stage, options, data: dict = {}, counter: int = 0):
        super().__init__(parent=parent, openfaults=openfaults, prevframe=prevframe)
        # print(f'options : {options}')
        self.options = options
        self.stage = stage
        # self.conditions = conditions
        self.data = data.copy()
        self.counter = counter
        self.islast = self.stage == openstages[-1]
        self.currentframe = self
        collength = 5
        iterable = self.getselection()
        print(f'iter {iterable}, {self.data}, {data}')
        if len(iterable) == 1:  # ERROR FIX THIS, CREATING BLANK FRAMES INSTEAD OF SKIPPING FRAME WITH ONLY 1 SELECTION!!
            self.currentframe = self.prevframe
            # self.pack_forget()
            # self.destroy()
            self.onbuttonpress(iterable[0])
            return

        # # DISPLAY CURRENT STAGE, SHOW WHAT WAS FILLED EARLIER.

        # frame1 = myframe(parent=self)
        # frame2 = myframe(parent=self)
        # tk.Label(master=self, text=engtohebdict[stage], fg="#DDDDDD",
        #          bg="#00ADB5", **regfont).grid(columnspan=2, pady=10)
        # frame1.grid(column=0)
        # frame2.grid(column=1)
        # for row, st in enumerate(openstages):
        #     # print(get_keys_from_value(engtohebdict,st))
        #     tk.Label(master=frame2, text=engtohebdict[st], bg=frame2['bg'], **
        #              regfont, fg='red' if self.stage == st else 'black').grid(row=row)

        # # CLEAN CODE TOMMOROW. MAYBE REPLACE TK.LABEL
        x = myframe(parent=self)
        for col, st in enumerate(openstages[::-1]):
            tk.Label(master=x, text=engtohebdict[st], fg="#DDDDDD" if self.stage == st else 'black',
                     bg="#00ADB5", **regfont).grid(padx=5, pady=(0, 10), column=col, row=0)
            if st in self.data:
                tk.Label(master=x, text=self.data[st], bg='#393E46',
                         fg='#00ADB5', **regfont).grid(padx=5, pady=(0, 10), column=col, row=1)
            else:
                tk.Label(master=x, text='', fg="#DDDDDD" if self.stage == st else 'black',
                         bg="#222831", **regfont).grid(padx=5, pady=(0, 10), column=col, row=1)
        x.grid()

        new_list = [iterable[i:i+collength]
                    for i in range(0, len(iterable), collength)]
        for row, tup in enumerate(new_list, 1):
            x = myframe(parent=self)
            [mybutton('#222831', x, text=opt, **regfont, fg="#00ADB5",
                      bg="#393E46", command=partial(self.onbuttonpress, opt)).grid(padx=5, row=0, column=col) for col, opt in enumerate(sorted(tup, reverse=True))]
            x.grid(row=row, pady=(0, 10))
        self.backbutton()

    def getselection(self) -> list:
        print(self.counter, self.stage)
        return list({key if self.stage == 'devicename' else val[self.stage] for key, val in self.options.items() if all(
            [val[dkey] == dval for dkey, dval in self.data.items()])}) if self.counter == 0 else self.options if isinstance(self.options, list) else list(self.options.keys())

    # def submit

    def onbuttonpress(self, opt):
        self.pack_forget()
        # if self.stage=='devicename':
        #     self.data.update({
        #                  self.options[opt]})
        if self.stage != 'devicename':
            self.data.update({self.stage: opt})
        # print(self.data, self.conditions)
        if self.islast:
            # print(f'self.data : {self.conditions}')
            # print(all((any((i[stage]!=self.data[stage] for stage in stages)) for i in self.openfaults)),self.openfaults)
            # FIX COMPARE TO PASS ON MISSING KEYS!
            if all((any((i[stage] != self.data[stage] for stage in openstages if stage in i)) for i in self.openfaults)):
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
        # options = config["devices"][self.conditions['devicetype']
        #                             ] if self.stage == 'devicename' else self.options  # if statement needs improvement
        options = self.options if self.counter == 0 else self.options[opt]
        if self.stage == 'devicename':
            self.data.update(options[opt])
            self.data.update({'devicename': opt})
            openfaultframe(parent=self.parent, openfaults=self.openfaults, prevframe=self.currentframe, stage=openstages[openstages.index(
                self.stage)+1], options=config["devices"][self.data['devicetype']], data=self.data, counter=self.counter+1).pack()
            return
        openfaultframe(parent=self.parent, openfaults=self.openfaults, prevframe=self.currentframe, stage=openstages[openstages.index(
            self.stage)+1], options=options, data=self.data, counter=self.counter).pack()


if __name__ == '__main__':
    configName = 'config.json'
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), configName), encoding='utf-8') as f:
        config = json.load(f)
    localjsonpath = config['localjson']
    openstages = ['devicetype',
                  'devicename', 'component', 'description']
    closestages = openstages[1:]+['techcomment']
    completedjsonpath = config['completedjson']
    engtohebdict = config['engtohebdict']
    root = tk.Tk()
    deletephoto = tk.PhotoImage(
        file=r"D:\Projects\Python\FaultsManager\Assets\delete.png")
    root.state('zoomed')
    root.title('תיעוד תקלות')
    regfont = {'font': (
        "calibri", 18)}
    # root.geometry('300x400')
    root.configure(bg='#222831')
    tk.Label(root, text=config['user'], font=(
        "calibri", 24, 'bold'), bg='#222831', fg='#00ADB5').pack(padx=200, pady=15)
    with open(localjsonpath, encoding='utf-8') as f:
        openingframe(root, [openfaultobject(i)
                     for i in json.load(f)]).pack()
    root.mainloop()
