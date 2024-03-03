# -*- coding: utf-8 -*
# module conduit_for_forge.py

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
]

from revitutils.unit import Unit

doc = DM.Instance.CurrentDBDocument  # Получение файла документа


# lev = []
# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     equipment = doc.GetElement(el_circuit.BaseEquipment.Id).Host.Id
# OUT = lev

# Получаем типоразмер 3D-кабель
conduitType_elementId = [con.Id for con in FEC(doc).OfClass(
    DB.Electrical.ConduitType) if con.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == '3D-кабель']

with DB.Transaction(doc, 'Create conduit') as t:
    t.Start()
    conduits = []
    for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
        # получили путь/траекторию цепи
        path = el_circuit.GetCircuitPath()
        for i in range(len(path) - 1):
            if path[i].DistanceTo(path[i + 1]) > 0.1:
                conduit = DB.Electrical.Conduit.Create(
                    doc,
                    conduitType_elementId[0],
                    path[i],
                    path[i + 1],
                    # Id уровня дозы, к которой подключена цепь
                    doc.GetElement(el_circuit.BaseEquipment.Id).Host.Id
                )
        # Диаметр (Размер по каталогу)
        # Присвоили коробу диаметр из списка каталога 9мм (номинальный, у которого наружный 16мм,
        # если в каталоге такого диаметра нет, то все, внутренний, наружный и по каратлогу будут 9мм,
        # если близок к имеющемуся, то будет выбран имеющийся из каталога)
                conduit.Parameter[DB.BuiltInParameter.RBS_CONDUIT_DIAMETER_PARAM].Set(Unit(doc, 9).internal)
        # получили дозу, к которой подключена цепь
                equipment = doc.GetElement(el_circuit.BaseEquipment.Id)
        # извлекли параметр Комментарии дозы
                if equipment.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString():
                    comment = equipment.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString()
                    conduits.append(comment)
            # и присвоили значение параметру Комментарии короба
                    conduit.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].Set(comment)
                # БУДОВА_Диаметр
                CircuitDiameter = el_circuit.LookupParameter('кабНаружный диаметр, мм').AsDouble()
                ConduitDiameter = conduit.LookupParameter('БУДОВА_Диаметр')
                if CircuitDiameter:
                    ConduitDiameter.Set(Unit(doc, CircuitDiameter).internal)
                else:
                    ConduitDiameter.Set('')
                # БУДОВА_Тип кабеля
                CircuitCable = el_circuit.LookupParameter('Тип кабеля')
                CircuitCableName = doc.GetElement(CircuitCable.AsElementId()).Name
                if CircuitCable:
                    conduit.LookupParameter('БУДОВА_Тип кабеля').Set(CircuitCableName)
                # Сечение кабеля (str) Ищет 'х' на русском (БУДОВА_Поперечное сечение Number)
                    e = CircuitCableName.rfind('х') + 1
                    conduit.LookupParameter('БУДОВА_Поперечное сечение').Set(
                        float(CircuitCableName[e:].replace(',', '.'))
                    )
                    # Количество жил (БУДОВА_Количество жил Integer)
                    conduit.LookupParameter('БУДОВА_Количество жил').Set(
                        int(CircuitCableName[e-2:e-1])
                    )
                else:
                    conduit.LookupParameter('БУДОВА_Тип кабеля').Set('')
                # Панель (БУДОВА_Панель Text)
                # присвоили имя нагрузки + типоразмер панели
                ElementBaseEquipment = doc.GetElement(el_circuit.BaseEquipment.Id)
                conduit.LookupParameter('БУДОВА_Панель').Set(
                    ElementBaseEquipment.Name + ', ' +
                    ElementBaseEquipment.Symbol.Parameter[DB.BuiltInParameter.ALL_MODEL_TYPE_NAME].AsString()
                    )
                # Нагрузка (БУДОВА_Нагрузка Text)
                # имя нагрузки + типоразмер нагрузки
                for el in el_circuit.Elements:
                    conduit.LookupParameter('БУДОВА_Нагрузка').Set(
                        el.Name + ', ' +
                        el.Symbol.Parameter[DB.BuiltInParameter.ALL_MODEL_TYPE_NAME].AsString()
                        )
                # БУДОВА_Длина
                koef_circuit = 1.05  # коэффициент запаса на длину цепи применяем к коробу
                leng = conduit.Parameter[DB.BuiltInParameter.CURVE_ELEM_LENGTH].AsDouble()  # параметр длина короба
                leng_with_koef = koef_circuit * Unit(doc, leng).display  # длина цепи с коэффициентом запаса
                conduit.LookupParameter('БУДОВА_Длина').Set(leng_with_koef)
                # БУДОВА_Единица измерения
                conduit.LookupParameter('БУДОВА_Единица измерения').Set('мм')
                # БУДОВА_Артикул
                CircuitArt = el_circuit.LookupParameter('кабТип, марка, обозначение документа, опросного листа').AsString()
                ConduitArt = conduit.LookupParameter('БУДОВА_Артикул')
                if CircuitArt:
                    ConduitArt.Set(CircuitArt)
                else:
                    ConduitArt.Set('')
                # БУДОВА_Масса
                СircuitMassa = el_circuit.LookupParameter('кабМасса единицы, кг/км число').AsDouble()
                СonduitMassa = conduit.LookupParameter('БУДОВА_Масса')
                if СircuitMassa:
                    СonduitMassa.Set(СircuitMassa)
                else:
                    СonduitMassa.Set('')
                # БУДОВА_Уровень оборудования
                LevelEquipment = el_circuit.LookupParameter('БУДОВА_Уровень оборудования').AsString()
                ConduitLevelEquipment = conduit.LookupParameter('БУДОВА_Уровень оборудования')
                if LevelEquipment:
                    ConduitLevelEquipment.Set(LevelEquipment)
                else:
                    ConduitLevelEquipment.Set('')
                # БУДОВА_Этаж
                Level = el_circuit.LookupParameter('БУДОВА_Этаж').AsString()
                if Level:
                    conduit.LookupParameter('БУДОВА_Этаж').Set(Level)
                else:
                    conduit.LookupParameter('БУДОВА_Этаж').Set('')
                # БУДОВА_Признак цепи
                FeatureCircuit = el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString()
                if FeatureCircuit:
                    conduit.LookupParameter('БУДОВА_Признак цепи').Set(FeatureCircuit)
                else:
                    conduit.LookupParameter('БУДОВА_Признак цепи').Set('')

                # БУДОВА_Группа
                Group = el_circuit.LookupParameter('БУДОВА_Группа').AsString()
                ConduitGroup = conduit.LookupParameter('БУДОВА_Группа')
                if Group:
                    ConduitGroup.Set(Group)
                else:
                    ConduitGroup.Set('')
                # conduits.append(conduit)

                # БУДОВА_Классификация нагрузок
                KlassifLoadsId = el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()
                if KlassifLoadsId.IntegerValue != -1:
                    conduit.LookupParameter('БУДОВА_Примечание').Set(
                        doc.GetElement(KlassifLoadsId).Name)

                # BDV_E000_ Номер квартиры
                NumberFlat =el_circuit.LookupParameter('BDV_E000_ Номер квартиры').AsString()
                if NumberFlat:
                    conduit.LookupParameter('BDV_E000_ Номер квартиры').Set(NumberFlat)

                # BDV_E000_Имя помещения
                NameRoom = el_circuit.LookupParameter('BDV_E000_Имя помещения').AsString()
                if NameRoom:
                    conduit.LookupParameter('BDV_E000_Имя помещения').Set(NameRoom)

                # БУДОВА_Наименование системы
                NameSystem = el_circuit.LookupParameter('БУДОВА_Наименование системы').AsString()
                if NameSystem:
                    conduit.LookupParameter('БУДОВА_Наименование системы').Set(NameSystem)
                
    t.Commit()

# OUT = conduits

# BDV_E000_ Номер квартиры
# BDV_E000_Имя помещения

# classif_nagr = []
# priznak_cepi = []
# group = []
# type_cabel = []
# uroven_oborudov = []
# massa = []
# zagolovok = []
# artikul = []
# edenica_izmereniya = []
# diametr = []
# dlina = []


# koef_circuit = 1.05  # коэффициент запаса на длину цепи
# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]  # Длина цепи полная
#     unit = parameter.GetUnitTypeId()
#     leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали длину цепи во внешние единицы/как на экране пользователя
#     leng_with_koef = koef_circuit * leng  # длина цепи с коэффициентом запаса
#     dlina.append([round(leng_with_koef, 1), el_circuit.Id])
# OUT = dlina

# # БУДОВА_Диаметр
#     if el_circuit.LookupParameter('кабНаружный диаметр, мм').AsDouble():
#         diametr.append([el_circuit.LookupParameter('кабНаружный диаметр, мм').AsDouble(), (doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name)])
#     else:
#         diametr.append('')
# OUT = diametr

# # БУДОВА_Единица измерения
#     if el_circuit.LookupParameter('кабЕдиница измерения').AsString():
#         edenica_izmereniya.append(el_circuit.LookupParameter('кабЕдиница измерения').AsString())
#     else:
#         edenica_izmereniya.append('')
# OUT = edenica_izmereniya

# # БУДОВА_Артикул
#     if el_circuit.LookupParameter('кабТип, марка, обозначение документа, опросного листа').AsString():
#         artikul.append(el_circuit.LookupParameter('кабТип, марка, обозначение документа, опросного листа').AsString())
#     else:
#         artikul.append('')
# OUT = artikul

# БУДОВА_Масса
#     if el_circuit.LookupParameter('кабМасса единицы, кг/км число').AsDouble():
#         massa.append([el_circuit.LookupParameter('кабМасса единицы, кг/км число').AsDouble()/1000, (doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name)])
#     else:
#         massa.append('')
# OUT = massa

# БУДОВА_Уровень оборудования
# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     if el_circuit.LookupParameter('БУДОВА_Уровень оборудования').AsString():
#         uroven_oborudov.append(el_circuit.LookupParameter('БУДОВА_Уровень оборудования').AsString())
#     else:
#         uroven_oborudov.append('')
# OUT = uroven_oborudov

# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     if el_circuit.LookupParameter('Тип кабеля'):
#         type_cabel.append(doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name)
#     else:
#         type_cabel.append('')
# OUT = type_cabel

# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     if el_circuit.LookupParameter('Тип кабеля'):
#         type_cabel.append(doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name)
#     else:
#         type_cabel.append('')
# OUT = type_cabel

# БУДОВА_Группа
# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     if el_circuit.LookupParameter('БУДОВА_Группа').AsString():
#         group.append(el_circuit.LookupParameter('БУДОВА_Группа').AsString())
#     else:
#         group.append('')
# OUT = group

# БУДОВА_Признак цепи
#     if el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString():
#         priznak_cepi.append(el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString())
#     else:
#         priznak_cepi.append('')
# OUT = priznak_cepi

# БУДОВА_Классификация нагрузок
    # if el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
    #     classif_nagr.append('')
    # else:
    #     classif_nagr.append(doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name)
