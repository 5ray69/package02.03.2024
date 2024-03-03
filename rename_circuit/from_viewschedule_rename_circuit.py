# module from_viewschedule_rename_circuit.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC

from user_warning_rename_circuit import ErrorElementNotInSchedule


class FromViewSchedule(object):

    def __init__(self, doc, strNameSchedule):
        self.strNameSchedule = strNameSchedule
        self.doc = doc
        self.viewSched = [viewSchedule for viewSchedule in FEC(self.doc).OfClass(DB.ViewSchedule)
                            if self.strNameSchedule in viewSchedule.Name][0]

    def getElementId(self, strNameElement):
        """
        возвращает ElementId из ключевой спецификации по ключевому имени элемента-строки
        """

        listName = [elId.Name for elId in FEC(self.doc, self.viewSched.Id).ToElements()]
        if strNameElement not in listName:
            raise ErrorElementNotInSchedule(self.strNameSchedule, strNameElement)

        return [elId for elId in FEC(self.doc, self.viewSched.Id).ToElements() if strNameElement in elId.Name][0]