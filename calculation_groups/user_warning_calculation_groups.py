# module user_warning.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Windows.Forms')
import System.Windows.Forms as WF


class ParametrGroupEmptyException(Exception):
    def __init__(self, one_circuit):
        self.message = "Внимание! \
                        \nЕсть цепи с незаполненным параметром БУДОВА_Группа.\
                        Например, цепь с Id: " + str(one_circuit.Id) \
                        + "\nЗаполните c помощью скрипта rename_circuit."
                        
        WF.MessageBox.Show(self.message)


class DoubleGroupsException(Exception):
    def __init__(self, group_str):
        self.message = "Внимание! \
                        \nЕсть две отдельные группы с одинаковым именем.\
                        \nИли соедините их в одну, или переименуйте одну из них.\
                        \nНапример, две отдельные группы с общим именем и коды \
                        \nих панелей для поиска:  "  + group_str
                        
        WF.MessageBox.Show(self.message)


class NoTypeCableException(Exception):
    def __init__(self, group_str):
        self.message = "Внимание! \
                        \nЕсть цепи, которым НЕ НАЗНАЧЕН ПАРАМЕТР Тип каблея.\
                        \nЗначит, не запускался скрипт rename_circuit.\
                        \nСостояние цепей, можно смотреть в специцикации 'Инф.Группы'. \
                        \nНе заполнены цепи у котороых 'БУДОВА_Группа' " + group_str
        WF.MessageBox.Show(self.message)


class NoTypeCableIdException(Exception):
    def __init__(self, strId):
        self.message = "Внимание! \
                        \nЕсть цепи, которым НЕ НАЗНАЧЕН ПАРАМЕТР Тип каблея.\
                        \nЗначит, не запускался скрипт rename_circuit.\
                        \nСостояние цепей, можно смотреть в специцикации 'Инф.Группы'. \
                        \nЦепь с Id номер:  " + strId
        WF.MessageBox.Show(self.message)


class MoreTwoSecheniyException(Exception):
    def __init__(self, group_str):
        self.message = "Внимание! \
                        \n БОЛЬШЕ ДВУХ различных значений В ОДНОЙ ГРУППЕ\
                        \n у электрических цпей в параметре Тип каблея\
                        \nСостояние цепей, можно смотреть в специцикации 'Инф.Группы'. \
                        \nСмотрите цепи у котороых 'БУДОВА_Группа' " + group_str
        WF.MessageBox.Show(self.message)
