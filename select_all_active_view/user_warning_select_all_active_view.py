# -*- coding: utf-8 -*-
# module user_warning_select_all_active_view.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorCircuitNoConect(Exception):
    def __init__(self, circuit):
        self.message = "Есть цепи неподключенные к панелям.\
                        \nCмотрите в диспетчере инженерных систем (F9)\
                        \nцепи с названием <без имени>.\
                        \nId не подключенной цепи: " + str(circuit.Id.IntegerValue) + ".\
                        \nПодключите цепи, потом запустите скрипт rename circuit и\
                        \nтогда можно будет запустить этот скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)
