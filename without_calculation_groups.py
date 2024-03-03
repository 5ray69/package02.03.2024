# module 078_09_calculation_groups.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

from calculation_groups.circuit_servis_calculation_groups import CircuitСontain
from calculation_groups.calculationGroups import CalculationGroups
from calculation_groups.user_warning_calculation_groups import NoTypeCableException, \
                                MoreTwoSecheniyException
from calculation_groups.my_sort import my_sort_group

doc = DM.Instance.CurrentDBDocument # Получение файла документа
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo


list_family_symbol = [family_symbol for family_symbol in FEC(doc).OfClass(DB.FamilySymbol) \
        if family_symbol.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == 'BDV_E000_Принципиальная схема освещения']

activ_view_drafting = doc.ActiveView

family_id = []
with DB.Transaction(doc, 'create_family') as t:
    t.Start()
    display_units = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()  # получили объект ForgeTypeId
    # 700 - начало отсчета по Х
    # задаем в мм, удобно для человека, а код переводит во внутренние единицы
    valueX = DB.UnitUtils.ConvertToInternalUnits(82000, display_units)

    calculationGroups = CalculationGroups(doc, uidoc)
    dict_group_str_max_dU = calculationGroups.get_value_max_dU_from_path_with_max_dU()

    for group_str in my_sort_group(dict_group_str_max_dU.keys()):
        # 1900 - смещение по Х
        valueX += DB.UnitUtils.ConvertToInternalUnits(1900, display_units)
        family_ = doc.Create.NewFamilyInstance(
                                    DB.XYZ(valueX, 50, 0),
                                    list_family_symbol[0],
                                    activ_view_drafting
        )
        family_.LookupParameter('BDV_E000_группа №').Set(group_str)

        # цепей может быть подключено к головной панели несколько, потому суммируем их мощность
        # отходящая цепь теущей группы от головной панели
        list_circuits_loads = calculationGroups.get_circuit_loads_from_panel_for_group()[group_str][0]
        act_power = sum([CircuitСontain(cir).get_active_power() for cir in list_circuits_loads])
        family_.LookupParameter('BDV_E000_Активная мощность кВт').Set(round(act_power, 2))

        # КОСИНУС
        full_power = sum([CircuitСontain(circ).get_full_power() for circ in list_circuits_loads])
        if full_power == 0:
            # если косинус сделать = 0, то ток в семействе будет деление на ноль, поэтому = 1
            family_.LookupParameter('BDV_E000_cos φ').Set(1)
        else:
            family_.LookupParameter('BDV_E000_cos φ').Set(round(act_power / full_power, 2))

        # ДЛИНА всех проводов какие только есть в группе
        # int чтоб избавиться от фотмата double "1.0"
        # family_.LookupParameter('BDV_E000_Длина кабеля сеч.1').Set(
        #     str(int(calculationGroups.get_length_by_groups_all_circuits()[group_str][0])))

        family_.LookupParameter('BDV_E000_Момент мощности').Set(calculationGroups.get_maxM_path_with_maxdU()[group_str])

        family_.LookupParameter('BDV_E000_dU').Set(round(dict_group_str_max_dU[group_str], 2))

        listElementId = calculationGroups.all_elidSechenia_in_group[group_str]
        dictLengths = calculationGroups.sumLengths_sechenya_in_groups[group_str]
        if not len(listElementId):
            raise NoTypeCableException(group_str)
        if len(listElementId) == 1:
            N_x_Sechenie = doc.GetElement(listElementId[0]).LookupParameter('кабКолво на сеч').AsString()
            family_.LookupParameter('BDV_E000_Сечение1').Set(
                    doc.GetElement(listElementId[0]).LookupParameter('кабКолво на сеч').AsString())
            family_.LookupParameter('BDV_E000_Длина кабеля сеч1').Set(str(int(dictLengths[str(listElementId[0].IntegerValue)][0])))
            family_.LookupParameter('BDV_E000_Тип изоляции кабеля1').Set(
                    doc.GetElement(listElementId[0]).LookupParameter('кабТип изоляции').AsString())
        if len(listElementId) == 2:
            family_.LookupParameter('BDV_E000_Сечение1').Set(
                    doc.GetElement(listElementId[0]).LookupParameter('кабКолво на сеч').AsString())
            family_.LookupParameter('BDV_E000_Сечение2').Set(
                    doc.GetElement(listElementId[1]).LookupParameter('кабКолво на сеч').AsString())
            family_.LookupParameter('BDV_E000_Длина кабеля сеч1').Set(str(int(dictLengths[str(listElementId[0].IntegerValue)][0])))
            family_.LookupParameter('BDV_E000_Длина кабеля сеч2').Set(str(int(dictLengths[str(listElementId[1].IntegerValue)][0])))
            family_.LookupParameter('BDV_E000_Тип изоляции кабеля1').Set(
                    doc.GetElement(listElementId[0]).LookupParameter('кабТип изоляции').AsString())
            family_.LookupParameter('BDV_E000_Тип изоляции кабеля2').Set(
                    doc.GetElement(listElementId[1]).LookupParameter('кабТип изоляции').AsString())
        if len(listElementId) > 2:
            raise MoreTwoSecheniyException(group_str)

        family_id.append(family_.Id)
    t.Commit()

OUT = family_id







# def my_sort_group(list_af):
#     my_dict = {}
#     my_dict['гр.'] = []
#     my_dict['гр.А'] = []

#     for stri in list_af:
#         if 'А' in stri:
#             let_dig = []
#             for let in stri:
#                 if let.isdigit():
#                     let_dig.append(let)
#             # если список цифр не пуст
#             if let_dig:
#                 my_dict['гр.А'].append(int(''.join(let_dig)))
#             else:
#                 my_dict['гр.А'].append(stri[3:])
#         else:
#             let_dig = []
#             for let in stri:
#                 if let.isdigit():
#                     let_dig.append(let)
#             # если список цифр не пуст
#             if let_dig:
#                 my_dict['гр.'].append(int(''.join(let_dig)))
#             else:
#                 my_dict['гр.'].append(stri[3:])

#     sort_list = []
#     # если список не пуст
#     if my_dict['гр.А']:
#         for int_el in sorted(my_dict['гр.А']):
#             sort_list.append('гр.' + str(int_el) + 'А')
#     if my_dict['гр.']:
#         for int_el in sorted(my_dict['гр.']):
#             sort_list.append('гр.' + str(int_el))

#     return sort_list


# list_a = ['гр.1', 'гр.12', 'гр.3', 'гр.44', 'гр.1А', 'гр.12А', 'гр.33А', 'гр.45А', 'гр.блок контроля загазованности']

# for group in my_sort_group(list_a):
#     print group

# # Результаты:
# # >>> 
# # гр.1А
# # гр.12А
# # гр.33А
# # гр.45А
# # гр.1
# # гр.3
# # гр.12
# # гр.44
# # гр.блок контроля загазованности
# # >>>
