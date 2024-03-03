# -*- coding: utf-8 -*
# module renameCircuitAboveLevel.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


class AboveLevel(object):
    def __init__(self, doc, element):
        self._doc = doc
        self.element = element

    def getNameLevel(self):
        z_element = round(self.element.Location.Point.Z, 3)
        # отметка самого нижнего уровня
        lev_elev_min = sorted([lev.Elevation for lev in FEC(doc).OfClass(DB.Level)])[0]
        # если край элемента ниже самого нижнего уровня
        if z_element < lev_elev_min:
            lev_elev_min_name = [lev.Name for lev in FEC(doc).OfClass(DB.Level) \
                                if round(lev.Elevation, 3) == round(lev_elev_min, 3)][0]
            return lev_elev_min_name
        else:
            # уровни, которые ниже отметки элемента
            levs_elev_below = [lev for lev in FEC(doc).OfClass(DB.Level) if lev.Elevation <= z_element]
            # минимальная разница между Z уровня и Z элемента
            min_difference = sorted([z_element - lev.Elevation for lev in levs_elev_below])[0]
            # имя уровня с короторым разница минимальная, над которым элемент
            lev_name = [lev.Name for lev in FEC(doc).OfClass(DB.Level) \
                        if round(z_element - lev.Elevation, 3) == round(min_difference, 3)][0]
            return lev_name



# OUT = []
# # категория Электрические цепи
# for circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     # УРОВНИ НАГРУЗОК
#     list_LevelId_Loads = []
#     # получаем нагрузку цепи
#     for faminstan in circuit.Elements:
#         if faminstan.Host:
#             list_LevelId_Loads.append(faminstan.Host.Id)
#         else:
#             raise ErrorNoneLevel(faminstan, faminstan.Id, AboveLevel(doc, faminstan).getNameLevel())

#     baseEquip = circuit.BaseEquipment
#     # после проверки неподключенных цепей, иначе у None нет атрибута Host
#     # если панель привязана к уровню
#     if baseEquip.Host:
#         if baseEquip.Host.Id in list_LevelId_Loads:
#             OUT.append("cтояк")
#             # if el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString() is None:
#             #     el_circuit.LookupParameter('БУДОВА_Признак цепи').Set('магистраль')
#         else:
#             OUT.append("магистраль")
#     else:
#         raise ErrorNoneLevel(baseEquip, baseEquip.Id, AboveLevel(doc, baseEquip).getNameLevel())



