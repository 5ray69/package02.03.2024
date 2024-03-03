# -*- coding: utf-8 -*
# module take_magistral.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

from rename_circuit.user_warning_rename_circuit import ErrorNumberStoyak, \
                                                        ErrorEmptyParameter


class FromUserFormNameMagistral(object):
    '''Извлекает имя мгистрали указанное в форме пользователем'''
    def __init__(self, doc, dict_1, dict_2, equipment):
        self.doc = doc
        self.dict_1 = dict_1
        self.dict_2 = dict_2
        self.equipment = equipment

    def get_magistral(self):
        name_level_specifikacyi = self.doc.GetElement(self.equipment.Parameter[
            DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
        number_stoyak = self.equipment.LookupParameter('BDV_E000_Номер стояка')
        if number_stoyak is None:
            raise ErrorEmptyParameter(self.equipment, self.equipment.Id)
        if number_stoyak.AsInteger() == 1:
            if name_level_specifikacyi not in self.dict_1:
                return False
            else:
                return self.dict_1[name_level_specifikacyi]
        elif number_stoyak.AsInteger() == 2:
            if name_level_specifikacyi not in self.dict_2:
                return False
            else:
                return self.dict_2[name_level_specifikacyi]
        else:
            raise ErrorNumberStoyak(self.equipment, self.equipment.Id)
