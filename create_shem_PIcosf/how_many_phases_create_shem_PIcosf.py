# -*- coding: utf-8 -*
# module how_many_phases_create_shem_PIcosf.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


class HowManyPhases(object):
    '''Извлекает количество включенных фаз в семействе'''
    def __init__(self, el):
        self.el = el

    def getCount(self):

        howManyPhases = 0

        if self.el.LookupParameter('BDV_E000_фаза А').AsInteger() == 1:
            howManyPhases +=1
        if self.el.LookupParameter('BDV_E000_фаза В').AsInteger() == 1:
            howManyPhases +=1
        if self.el.LookupParameter('BDV_E000_фаза С').AsInteger() == 1:
            howManyPhases +=1

        return howManyPhases