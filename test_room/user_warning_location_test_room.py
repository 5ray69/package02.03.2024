# -*- coding: utf-8 -*-
# module user_warning_location_test_room.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorXYZSpatialElementOrPointLocation(Exception):
    def __init__(self, familyinstance):
        self.message = "У элемента c Id: " + str(familyinstance.Id.IntegerValue) + "\
                        \nотсутсвует точка принадлежности помещению и\
                        \nточка размещения семейства"
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorXYZSpatialElement(Exception):
    def __init__(self, familyinstance):
        self.message = "У элемента c Id: " + str(familyinstance.Id.IntegerValue) + "\
                        \nотсутсвует точка принадлежности помещению"
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorPointLocationPoint(Exception):
    def __init__(self, familyinstance):
        self.message = "У элемента c Id: " + str(familyinstance.Id.IntegerValue) + "\
                        \nотсутсвует точка размещения семейства"
        System.Windows.Forms.MessageBox.Show(self.message)
