# -*- coding: utf-8 -*
# module rename_circuit.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List
import json

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

from revitutils.unit import Unit
from rename_circuit.user_form_rename_circuit import User_input_form, ErrorCircuitNoConect, ErrorEnglishLetter


# DESERIALIZATION
# FOR DYNAMO читаем файл из текущей дирректории
with open(IN[0].DirectoryName + r'\rename_circuit\drop_list.json', 'r') as file:
    Dict_from_json = json.load(file)

user_form = User_input_form(Dict_from_json)
user_form.ShowDialog()
# di = user_form.dict_user_select
# словарь основного стояка
dict_1 = user_form.dict_user_select["1"]
# словарь второго стояка
dict_2 = user_form.dict_user_select["2"]

# все номера панелей, которые <= Npanels относятся К ПЕРВОЙ ЧАСТИ ЗДАНИЯ и для них словарь dict_1
# если в здании только один стояк щитов ШЭ (одна часть здания), то просто увеличь это число,
# чтоб из второго словаря не брались значения
Npanels = int(user_form.number_panels)

# SERIALIZATION ЗАПОМИНАЕМ ВЫБОР ПОЛЬЗОВАТЕЛЯ
# FOR DYNAMO создаем файл json в текущей дирректории, существующий с тем же именем перезапишется
with open(IN[0].DirectoryName + r'\rename_circuit\drop_list.json', 'w') as file:
    json.dump(user_form.dict_user_select, file, indent=4)

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo
answe = {}
for equip in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
    # у вложенных семейств нет значения параметра "Уровень спецификации" потому его извлечение дает -1 (InvalidElementId)
    # если семейство не вложенное
    if equip.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
        # Если параметр "Имя панели" заполнен
        if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() is not None:
            old_name = equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
            # если есть английская M или А в имени
            if 'M' in old_name or 'A' in old_name:
                raise ErrorEnglishLetter(old_name, equip.Id)

            # если в имени панели есть 'ЩЭ'
            if 'ЩЭ' in equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString():
                # значение параметра Уровень спецификации
                curent_level = doc.GetElement(equip.Parameter[
                DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name

                # заполняем параметр БУДОВА_Обозначение щитов этажных
                if equip.Symbol.LookupParameter('БУДОВА_Количество счетчиков'):
                    if curent_level[1:2] == '0':
                        str_name = 'ЩЭ' + ' ' + str(equip.Symbol.LookupParameter('БУДОВА_Количество счетчиков').AsInteger()) + '-' + curent_level[2:3]
                        equip.LookupParameter('БУДОВА_Обозначение').Set(str_name)
                    else:
                        str_name = 'ЩЭ' + ' ' + str(equip.Symbol.LookupParameter('БУДОВА_Количество счетчиков').AsInteger()) + '-' + curent_level[1:3]
                        equip.LookupParameter('БУДОВА_Обозначение').Set(str_name)

                # первый стояк ЩЭ
                if equip.LookupParameter('BDV_E000_номер_стояка').AsInteger() == 1:
                    # old_name[old_name.rfind('/'):] - взяли все что после символа '/'
                    # curent_level[1:3] - взяли две цифры этажа из имени уровня
                    # dict_1[curent_level] - взяли значение магистрали соответсвующее этажу из словаря
                    # новое значение параметру "Имя панели"
                    new_name = dict_1[curent_level] + '-' + curent_level[1:3] + old_name[old_name.rfind('/'):]
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                    equip.LookupParameter('БУДОВА_Группа').Set(new_name)
                    equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                    equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                    # взяли из имени цепи номер магистрали и вписали в имя панели
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(old_name[:2] + dict_1[curent_level][1:] + '.' + curent_level[1:3])

                # второй стояк ЩЭ
                if equip.LookupParameter('BDV_E000_номер_стояка').AsInteger() == 2:
                    new_name = dict_2[curent_level] + '-' + curent_level[1:3] + old_name[old_name.rfind('/'):]
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                    equip.LookupParameter('БУДОВА_Группа').Set(new_name)
                    equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                    equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(old_name[:2] + dict_2[curent_level][1:] + '.' + curent_level[1:3])

                # все цепи нагрузок щита
                for el_circuit in equip.MEPModel.GetAssignedElectricalSystems():
                    # коэффициент запаса на длину цепи
                    koef_circuit = 1.05
                    # длина цепи переведем в метры (int чтобы избавиться от формата double "1.0" - получить целое число )
                    len = int(round(koef_circuit * Unit(doc, el_circuit.Parameter[
                        DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM].AsDouble(), False).display / 1000))
                    # цвета марки панели черный
                    if len < 25:
                        equip.LookupParameter('БУДОВА_Black').Set(1)
                        equip.LookupParameter('БУДОВА_Red').Set(0)
                        equip.LookupParameter('БУДОВА_Green').Set(0)
                        # если параметр 'Тип кабеля' не заполнен
                        if el_circuit.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                            # присваиваем значение 'ВВГнг-LS 3х10' ElementId 356553
                            el_circuit.LookupParameter('Тип кабеля').Set(DB.ElementId(356553))
                    # цвета марки панели красный
                    if 25 <= len < 40:
                        equip.LookupParameter('БУДОВА_Black').Set(0)
                        equip.LookupParameter('БУДОВА_Red').Set(1)
                        equip.LookupParameter('БУДОВА_Green').Set(0)
                        # если параметр 'Тип кабеля' не заполнен
                        if el_circuit.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                            # присваиваем значение 'ВВГнг-LS 3х16' ElementId 356554
                            el_circuit.LookupParameter('Тип кабеля').Set(DB.ElementId(356554))
                    # цвета марки панели зеленый
                    if len >= 40:
                        equip.LookupParameter('БУДОВА_Black').Set(0)
                        equip.LookupParameter('БУДОВА_Red').Set(0)
                        equip.LookupParameter('БУДОВА_Green').Set(1)
                        # если параметр 'Тип кабеля' не заполнен
                        if el_circuit.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                            # присваиваем значение 'ВВГнг-LS 3х25' ElementId 356572
                            el_circuit.LookupParameter('Тип кабеля').Set(DB.ElementId(356572))
                    # присваивам значение 'БУДОВА_Тип кабеля' для марки в схему
                    equip.LookupParameter('БУДОВА_Тип кабеля').Set(
                        equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() + ' - ' + 
                        doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name + 
                        ' L = ' + str(len) + 'м')

            # если в имени панели нет 'ЩЭ'
            else:
                # из имени панели ".этаж" отбросили и вместо них вписали точку + этаж из текущего уровня
                new_name = old_name[:old_name.rfind('.')] + '.' + curent_level[1:3]
                equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                # equip.LookupParameter('БУДОВА_Группа').Set(new_name)
                equip.LookupParameter('БУДОВА_Группа').Set(old_name[:old_name.rfind('.')])
                equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
            # если значение параметра "Обозначение цепей" С перфиксами ElementId -7000010 (По проекту ElementId -7000014),(Параметр не заполнен ElementId <null>)
            if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAMING].AsElementId().IntegerValue == -7000010:
                # параметр Префикс цепи создаем из нового этажа, после копирования
                # название эл.цепи меняется с изменением префикса
                equip.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_PREFIX].Set(
                    old_name[:old_name.rfind('.')] + '.' + curent_level[1:3] + 'эт_цепь')



                else:
                    # из имени панели ".этаж" отбросили и вместо них вписали точку + этаж из текущего уровня
                    new_name = old_name[:old_name.rfind('.')] + '.' + curent_level[1:3]
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                    # equip.LookupParameter('БУДОВА_Группа').Set(new_name)
                    equip.LookupParameter('БУДОВА_Группа').Set(old_name[:old_name.rfind('.')])
                    equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                    equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                # если значение параметра "Обозначение цепей" С перфиксами ElementId -7000010 (По проекту ElementId -7000014),(Параметр не заполнен ElementId <null>)
                if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAMING].AsElementId().IntegerValue == -7000010:
                    # параметр Префикс цепи создаем из нового этажа, после копирования
                    # название эл.цепи меняется с изменением префикса
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_PREFIX].Set(
                        old_name[:old_name.rfind('.')] + '.' + curent_level[1:3] + 'эт_цепь')






with DB.Transaction(doc, 'RenameСircuit') as t:
    t.Start()
    # категория Электрооборудование
    # для всех элементов категории Электрооборудование, которые не являются вложенным семейством
    for equip in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
        # у вложенных семейств нет значения параметра "Уровень спецификации" потому его извлечение дает -1 (InvalidElementId)
        # если семейство не вложенное
        if equip.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
            # значение параметра Уровень спецификации
            curent_level = doc.GetElement(equip.Parameter[
                DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
            # Если параметр "Имя панели" заполнен
            if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() is not None:
                # значение параметра Имя панели
                old_name = equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
                # если есть английская M в имени
                if 'M' in old_name or 'A' in old_name:
                    raise ErrorEnglishLetter(old_name, equip.Id)
                # если в имени панели есть 'М' русская
                if 'М' in old_name and 'Щ' not in old_name:
                    # все номера панелей, которые <= Npanels относятся К ПЕРВОЙ ЧАСТИ ЗДАНИЯ и для них словарь dict_1
                    # если в здании только один стояк щитов ШЭ (одна часть здания), то просто увеличь это число,
                    # чтоб из второго словаря не брались значения
                    if int(old_name[old_name.rfind('/') + 1:]) <= Npanels:
                        # old_name[old_name.rfind('/'):] - взяли все что после символа '/'
                        # curent_level[1:3] - взяли две цифры этажа из имени уровня
                        # dict_1[curent_level] - взяли значение магистрали соответсвующее этажу из словаря
                        # новое значение параметру "Имя панели"
                        new_name = dict_1[curent_level] + '-' + curent_level[1:3] + old_name[old_name.rfind('/'):]
                        equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                        equip.LookupParameter('БУДОВА_Группа').Set(new_name)
                        equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                        equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                    else:
                        new_name = dict_2[curent_level] + '-' + curent_level[1:3] + old_name[old_name.rfind('/'):]
                        equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                        equip.LookupParameter('БУДОВА_Группа').Set(new_name)
                        equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                        equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                    # получили электрические цепи присоединенные к электрооборудованию
                    for el_circ in equip.MEPModel.GetElectricalSystems():
                        # если в имени цепи есть 'М' русская и '/'
                        if 'М' in el_circ.Name and '/' in el_circ.Name:
                            # коэффициент запаса на длину цепи
                            koef_circuit = 1.05
                            # длина цепи переведем в метры (int чтобы избавиться от формата double "1.0" - получить целое число )
                            len = int(round(koef_circuit * Unit(doc, el_circ.Parameter[
                                DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM].AsDouble(), False).display / 1000))
                            # цвета марки панели черный
                            if len < 25:
                                equip.LookupParameter('БУДОВА_Black').Set(1)
                                equip.LookupParameter('БУДОВА_Red').Set(0)
                                equip.LookupParameter('БУДОВА_Green').Set(0)
                                # если параметр 'Тип кабеля' не заполнен
                                if el_circ.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                                    # присваиваем значение 'ВВГнг-LS 3х10' ElementId 356553
                                    el_circ.LookupParameter('Тип кабеля').Set(DB.ElementId(356553))
                            # цвета марки панели красный
                            if 25 <= len < 40:
                                equip.LookupParameter('БУДОВА_Black').Set(0)
                                equip.LookupParameter('БУДОВА_Red').Set(1)
                                equip.LookupParameter('БУДОВА_Green').Set(0)
                                # если параметр 'Тип кабеля' не заполнен
                                if el_circ.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                                    # присваиваем значение 'ВВГнг-LS 3х16' ElementId 356554
                                    el_circ.LookupParameter('Тип кабеля').Set(DB.ElementId(356554))
                            # цвета марки панели зеленый
                            if len >= 40:
                                equip.LookupParameter('БУДОВА_Black').Set(0)
                                equip.LookupParameter('БУДОВА_Red').Set(0)
                                equip.LookupParameter('БУДОВА_Green').Set(1)
                                # если параметр 'Тип кабеля' не заполнен
                                if el_circ.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                                    # присваиваем значение 'ВВГнг-LS 3х25' ElementId 356572
                                    el_circ.LookupParameter('Тип кабеля').Set(DB.ElementId(356572))
                            # присваивам значение 'БУДОВА_Тип кабеля' для марки в схему
                            equip.LookupParameter('БУДОВА_Тип кабеля').Set(
                                equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() + ' - ' + 
                                doc.GetElement(el_circ.LookupParameter('Тип кабеля').AsElementId()).Name + 
                                ' L = ' + str(len) + 'м')
                else:
                    # из имени панели ".этаж" отбросили и вместо них вписали точку + этаж из текущего уровня
                    new_name = old_name[:old_name.rfind('.')] + '.' + curent_level[1:3]
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                    # equip.LookupParameter('БУДОВА_Группа').Set(new_name)
                    equip.LookupParameter('БУДОВА_Группа').Set(old_name[:old_name.rfind('.')])
                    equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                    equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                # если значение параметра "Обозначение цепей" С перфиксами ElementId -7000010 (По проекту ElementId -7000014),(Параметр не заполнен ElementId <null>)
                if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAMING].AsElementId().IntegerValue == -7000010:
                    # параметр Префикс цепи создаем из нового этажа, после копирования
                    # название эл.цепи меняется с изменением префикса
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_PREFIX].Set(
                        old_name[:old_name.rfind('.')] + '.' + curent_level[1:3] + 'эт_цепь')





    circuit_no_conect = []
    # категория Электрические цепи
    for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
        if 'M' in el_circuit.Name or 'A' in el_circuit.Name:
            raise ErrorEnglishLetter(el_circuit.Name, el_circuit.Id)
        if hasattr(el_circuit.BaseEquipment, 'Parameter'):
            # если значение параметра панели "Обозначение цепей" По проекту ElementId -7000014 (С перфиксами ElementId -7000010),(Параметр не заполнен ElementId <null>)
            if el_circuit.BaseEquipment.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAMING].AsElementId().IntegerValue == -7000014:
                # получаем нагрузку цепи
                for faminstan in el_circuit.Elements:
                    # имя нагрузки записали в параметр цепи "Имя нагрузки"
                    el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(faminstan.Name)
            # Обновляем документ чтоб вступили в силу новые имена цепей, иначе придется запускать скрипт дважды
            doc.Regenerate()

            # Присваиваем значение тип кабеля цепям подключающим коробки КК
            # если КК содержится в имени нагрузки цепи
            if 'КК' in el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].AsString():
                # если параметр 'Тип кабеля' не заполнен
                if el_circuit.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                    # присваиваем значение 'ПВ 1х4' ElementId 356542
                    el_circuit.LookupParameter('Тип кабеля').Set(DB.ElementId(356542))

            # этаж и увровень оборудования заполняем из панели цепи
            el_circuit.LookupParameter('БУДОВА_Этаж').Set(el_circuit.BaseEquipment.Host.Name)
            el_circuit.LookupParameter('БУДОВА_Уровень оборудования').Set(el_circuit.BaseEquipment.Host.Name[1:3])
            # если в имени цепи есть английская или русская точка "." (для всего что не магистрали квартир)
            if '.' in el_circuit.Name or '.' in el_circuit.Name: 
                number_circuit = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
                el_circuit.LookupParameter('БУДОВА_Группа').Set(number_circuit[:number_circuit.rfind('.')])
            # если в имени цепи есть "/" (для магистралей квартир)
            if '/' in el_circuit.Name:
                number_circuit = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
                el_circuit.LookupParameter('БУДОВА_Группа').Set(number_circuit[:number_circuit.rfind('э')])
            # если в имени цепи есть "гр"
            if 'гр' in el_circuit.Name:
                # получаем нагрузку цепи
                for faminstan in el_circuit.Elements:
                    # имя нагрузки записали в параметр цепи "Имя нагрузки"
                    el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(faminstan.Name)
                # если параметр 'БУДОВА_Признак цепи' не заполнен
                if el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString() is None:
                    el_circuit.LookupParameter('БУДОВА_Признак цепи').Set('магистраль')
                # если параметр 'БУДОВА_Классификация нагрузок' не заполнен
                if el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
                    # присваиваем ему значение 'Освещение' ElementId 155010
                    el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').Set(DB.ElementId(155010))
                # если параметр 'Тип кабеля' не заполнен
                if el_circuit.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                    # если в имени цепи есть 'A' русская
                    if 'A' in el_circuit.Name:
                        # присваиваем значение 'FLAME 3х2,5' ElementId 356558
                        el_circuit.LookupParameter('Тип кабеля').Set(DB.ElementId(356558))
                    else:
                        # присваиваем значение 'ВВГнг-LS 3х2,5' ElementId 356552
                        el_circuit.LookupParameter('Тип кабеля').Set(DB.ElementId(356552))
                # Все что не стояк – группа, для различных коэффициентов длины
                el_circuit.LookupParameter('БУДОВА_Group').Set(1)
            else:
                # все что не содержит "гр." будет с другим коэф. длины
                el_circuit.LookupParameter('БУДОВА_Group').Set(0)
        else:
            circuit_no_conect.append([el_circuit, 'цепь не подключена к панели'])

# # Светильники, выключатели, розетки, ЯТП
#     categories = [
#         DB.BuiltInCategory.OST_ElectricalFixtures,  # здесь вложенные семейства (другой подход) электрические проборы
#         DB.BuiltInCategory.OST_LightingDevices,  # здесь БЕЗ вложенных семейств (один подход) выключатели
#         DB.BuiltInCategory.OST_LightingFixtures,  # здесь БЕЗ вложенных семейств (один подход) осветительные приборы
#     ]
#     element_no_connect = []
#     multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))
#     for elem in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():
#         # если есть значение параметра Уровень спецификации - так исключаем вложенные семейства
#         if elem.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
#             # значение параметра Уровень спецификации
#             level_spec = doc.GetElement(elem.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
#             elem.LookupParameter('БУДОВА_Этаж').Set(level_spec)
#             elem.LookupParameter('БУДОВА_Уровень оборудования').Set(level_spec[1:3])
#             # если значение параметра Номер цепи
#             number_circuit = elem.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
#             elem.LookupParameter('БУДОВА_Группа').Set(number_circuit[:number_circuit.rfind('.')])
#             # если значение параметра Номер цепи пустая строка, то элемент не подключен
#             if number_circuit == "":
#                 element_no_connect.append([elem, elem.Id, level_spec, 'не подключен'])

    # категория Электрооборудование для переименования ЩЭ (ЗАМЕНИТЬ НА ЭЩ) на основе вышепроизведенных в скрипте преобразований
    for equip in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
        # у вложенных семейств нет значения параметра "Уровень спецификации" потому его извлечение дает -1 (InvalidElementId)
        # если семейство не вложенное
        if equip.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
            # значение параметра Уровень спецификации
            curent_level = doc.GetElement(equip.Parameter[
                DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
            # Если параметр "Имя панели" заполнен
            if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() is not None:
                # значение параметра Имя панели
                old_name = equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
                # если в имени панели есть 'ЩЭ' (ЗАМЕНИТЬ НА ЭЩ)
                if 'ЩЭ' in old_name:
                    # получили электрические цепи присоединенные к электрооборудованию
                    for el_circ in equip.MEPModel.GetElectricalSystems():
                        # выбрали имя первой цепи подключенной к щиту, которая содержит 'М'
                        # если в имени цепи есть 'М' русская и '/'
                        if 'М' in el_circ.Name and '/' in el_circ.Name:
                            # взяли из имени цепи номер магистрали и вписали в имя панели
                            equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(old_name[:2] + el_circ.Name[1:el_circ.Name.rfind('-')] + old_name[old_name.rfind('.'):])
                            # после выполнения первой итеррации обрываем цикл, берем только одну цепь из всех подключенных к щиту
                            break
                    # заполняем параметр БУДОВА_Обозначение щитов этажных
                    if equip.Symbol.LookupParameter('БУДОВА_Количество счетчиков'):
                        if curent_level[1:2] == '0':
                            str_name = 'ЭЩ' + ' ' + str(equip.Symbol.LookupParameter('БУДОВА_Количество счетчиков').AsInteger()) + '-' + curent_level[2:3]
                            equip.LookupParameter('БУДОВА_Обозначение').Set(str_name)
                        else:
                            str_name = 'ЭЩ' + ' ' + str(equip.Symbol.LookupParameter('БУДОВА_Количество счетчиков').AsInteger()) + '-' + curent_level[1:3]
                            equip.LookupParameter('БУДОВА_Обозначение').Set(str_name)

#     # выводим список неподсоединенных устройств и цепей
#     OUT = element_no_connect, circuit_no_conect
#     t.Commit()
# if circuit_no_conect:
#     ErrorCircuitNoConect()


# черновой рассчет стояков в экселе, а затем уточненный расчет в экселе после получения длин из ревита
# переименовать трубы
