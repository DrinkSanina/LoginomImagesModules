import builtin_data
from builtin_data import InputTable, InputTables, InputVariables, OutputTable, DataType, DataKind, UsageType
import numpy as np, pandas as pd
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table

import pandas as pd
import tkinter as tk
import tkinter.filedialog as fd
from tkinter import *

import re

from configparser import ConfigParser
import platformdirs
import os


# Код класса поля с автозаполнением - для выбора минералов из списка ###########

class AutocompleteEntry(Entry):
    def __init__(self, autocompleteList, *args, **kwargs):
        # Listbox length
        if 'listboxLength' in kwargs:
            self.listboxLength = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.listboxLength = 8

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)
                
            self.matchesFunction = matches

        
        Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.autocompleteList = autocompleteList
        
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)
        
        self.listboxUp = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if not self.listboxUp:
                    self.listbox = Listbox(width=self["width"], height=self.listboxLength)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.listboxUp = True
                
                self.listbox.delete(0, END)
                for w in words:
                    self.listbox.insert(END,w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False
        
    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(ACTIVE))
            self.listbox.destroy()
            self.listboxUp = False
            self.icursor(END)

    def moveUp(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != '0':                
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def moveDown(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != END:                        
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index) 

    def comparison(self):
        return [ w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w) ]
    
    def change_autocompletelist(self,value):
        self.autocompleteList = value

if __name__ == '__main__':
    def matches(fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)
    
################################################################################

# Название папки, которая будет создана в %APPDATA%
appname = 'MineralsImageAddon'
configfile = os.path.join(os.environ['APPDATA'],appname,"config.ini")
namespath = ""
autocompleteList = []

# Функция, позволяющая выбрать файл с именем базы минералов
def choose_namebase(entry):
    file_path = fd.askopenfilename(parent=root, title='Выберите файл', filetypes=[('Текстовый файл','*.txt')])
    if file_path:
        with open(file_path, 'r') as file:
            lines = [line.rstrip() for line in file]
            entry.change_autocompletelist(lines) # Заполнить список автозаполнения
        # Прописать путь к файлу с именем минералов, чтобы не вводить его заново
        config = ConfigParser()
        config.read(configfile)
        config.set('Mineral_Names', 'filepath', file_path)
        with open(configfile, 'w') as f:
            config.write(f)

# Функция, запускаемая в конце работы - вносит имя минерала в вывод
def choose_mineral(root, mineral_name):
    if(mineral_name != ""):
        print(mineral_name)
        output_frame = pd.DataFrame({'Mineral_name': [mineral_name]})
        fill_table(OutputTable, output_frame, with_index=False)

        # Очень важная строчка при работе с внешними формами Tkinter:
        # без неё форма никогда не закроется и узел будет невозможно активировать
        # ещё раз
        root.destroy() 

# Если папки с названием MineralsImageAddon нет в Appdata, то создать её
if not os.path.exists(os.path.join(os.environ['APPDATA'],appname)):
    os.mkdir(os.path.join(os.environ['APPDATA'],appname))

if not os.path.exists(configfile):
    open(configfile, 'a').close()                 #Если файла конфигурации нет,
    config = ConfigParser()                       #то создать пустой и добавить
    config.read(configfile)                       #в него секцию Mineral_Names
    config.add_section('Mineral_Names')                  
    config.set('Mineral_Names', 'filepath', '0')  
    with open(configfile, 'w') as f:              
        config.write(f)
else:                                             #Если файл конфигурации есть
    config = ConfigParser()                       #то считать с него путь к файлу
    config.read(configfile)                       #c именами минералов
    namespath = config.get("Mineral_Names", "filepath")
    if(namespath != "0"):
        if os.path.exists(namespath):
            with open(namespath, 'r') as file:
                lines = [line.rstrip() for line in file]
                autocompleteList = lines
            
# Создание экзкмпляра окна Tkinter
root = tk.Tk()

# построение формы
root.title("Справочник имен минералов")
root.geometry("400x200")

entry = AutocompleteEntry(autocompleteList, root, listboxLength=6, width=32, matchesFunction=matches)
entry.pack(padx=6, pady=6)

btn = tk.Button(text="Выбрать файл базы имен минералов", command=lambda: choose_namebase(entry))
btn.pack(padx=6,pady=6)

btn2 = tk.Button(text="Выбрать минерал", command=lambda: choose_mineral(root, entry.get()))
btn2.pack(padx=6,pady=6)


root.mainloop()