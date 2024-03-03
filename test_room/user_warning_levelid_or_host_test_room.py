# -*- coding: utf-8 -*-
# module user_warning_levelid_or_host_test_room.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorElementDoesNotHaveLevel(Exception):
    def __init__(self, elem):
        self.message = "У элемента c Id: " + str(elem.Id.IntegerValue) + "\
                        \nне удалось извлечь уровень. \
                        \n \
                        \nВозможно, элемент не привязан к рабочей плоскоски.\
                        \nЗадайте рабочую плоскость и запустие скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)
