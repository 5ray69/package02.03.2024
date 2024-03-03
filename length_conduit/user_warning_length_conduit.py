# -*- coding: utf-8 -*-
# module user_warning_create_circuit_stoyak_floor_shield.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorEmptyParamGroup(Exception):
    def __init__(self, el, levCond, elementId):
        self.message = "Параметр 'БУДОВА_Группа' не заполнен\
                        \nу элемента: " + el.Category.Name + ",\
                        \nc Id: " + str(elementId.IntegerValue) + ".\
                        \nПривязан к уровню: " + levCond + ".\
                        \nЗаполните параметр и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)
