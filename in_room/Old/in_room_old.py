# -*- coding: utf-8 -*
# module in_room.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List
# import json

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo

from in_room.user_warning_in_room import ErrorThereAreNoLevels, ErrorThereAreNoLinkDoc,\
                                        ErrorEmptyParameter

# экземпляр связи
LinkInstance = [LinkInstan for LinkInstan in FEC(doc).OfClass(DB.RevitLinkInstance) if "отсоединено" in LinkInstan.Name][0]
# ЕСЛИ ФАЙЛ СВЯЗИ НЕ БУДЕТ НАЙДЕН ПО ИМЕНИ
if not LinkInstance:
    raise ErrorThereAreNoLinkDoc()
# документ связи
LinkDoc = LinkInstance.GetLinkDocument()
# # типоразмер связи
# LinkType = doc.GetElement(LinkInstance.GetTypeId())
# трансформация из связи
LinkTransform = LinkInstance.GetTotalTransform()


# ПРОВЕРКА НАЛИЧИЯ УРОВНЕЙ СВЯЗИ В ОСНОВНОМ ФАЙЛЕ
LevelsChifFile = [level.Name for level in FEC(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType()]
LevelsLink = [leve.Name for leve in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType()]
NotInList = []
for levName in LevelsLink:
    if levName not in LevelsChifFile:
        NotInList.append(levName)
OUT = LevelsLink
if NotInList:
    raise ErrorThereAreNoLevels(NotInList)

# OUT = [[room.LookupParameter('БУДОВА_Номер квартиры').AsString(), room.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString(), room.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString()] for room in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_Rooms)]
# OUT = [room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString() for room in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_Rooms)]
# OUT = [room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString() for room in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment)]



categories = [
    DB.BuiltInCategory.OST_ElectricalFixtures,  # здесь вложенные семейства (другой подход) электрические приборы
    DB.BuiltInCategory.OST_ElectricalEquipment,  # здесь вложенные семейства (другой подход) электрооборудование
    DB.BuiltInCategory.OST_LightingDevices,  # здесь без вложенных семейств (один подход) выключатели
    DB.BuiltInCategory.OST_LightingFixtures,  # здесь без вложенных семейств (один подход) осветительные приборы
    DB.BuiltInCategory.OST_Conduit,  # здесь без вложенных семейств (один подход) короба
    DB.BuiltInCategory.OST_ConduitFitting,  # без вложенных семейств (один подход) соденительные детали коробов
    DB.BuiltInCategory.OST_CableTray,  # без вложенных семейств (один подход) кабельные лотки
    DB.BuiltInCategory.OST_CableTrayFitting,  # здесь вложенные семейства  (другой подход)соденительные детали кабельных лотков
    DB.BuiltInCategory.OST_ElectricalCircuit,  # электрические цепи
    DB.BuiltInCategory.OST_FireAlarmDevices  # без вложенных семейств (один подход) пожарная сигнализация
]

multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))
OUT = []
with DB.Transaction(doc, 'in_room') as t:
    t.Start()
    for room in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_Rooms):
        RoomName = room.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()
        FlatNumber = room.LookupParameter('БУДОВА_Номер квартиры').AsString()
        RoomNumber = room.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString()
        for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():
            # ПОЛОСА ЗАЗЕМЛЕНИЯ, КАТЕГОРИЯ ПОЖАРНАЯ СИГНАЛИЗАЦИЯ
            if el.Category.Id.IntegerValue == -2008085:
                # если 'БУДОВА_Этаж' не заполнен (никогда не заполнялся или затерт)
                if el.LookupParameter('БУДОВА_Этаж').AsString() is None \
                            or not el.LookupParameter('БУДОВА_Этаж').AsString():
                    raise ErrorEmptyParameter(el, el.Id)
                # если этаж полосы заземления равен этажу помещения
                if el.LookupParameter('БУДОВА_Этаж').AsString() == room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString():
                    # точки из файла электрика приводим к координатам связи
                    if room.IsPointInRoom(LinkTransform.OfPoint(el.Location.Curve.GetEndPoint(0))) or room.IsPointInRoom(LinkTransform.OfPoint(el.Location.Curve.GetEndPoint(1))):
                        if RoomName:
                            el.LookupParameter('BDV_E000_Имя помещения').Set(RoomName)
                        if FlatNumber:
                            el.LookupParameter('БУДОВА_Номер квартиры').Set(FlatNumber)
                        if RoomNumber:
                            el.LookupParameter('BDV_E000_Номер помещения').Set(RoomNumber)

            # КОРОБА И КАБЕЛЬНЫЕ ЛОТКИ
            # у соед.деталей коробов и кабельных лотков нет параметра Уровень спецификации, а есть параметр Базовый уровень
            # потому нужна отдельная обработка
            # если выполняется любое из условий (аналогично функция all - выполняются все условия)
            if any([
                isinstance(el, DB.Electrical.Conduit),
                isinstance(el, DB.Electrical.CableTray)
                ]):
                # если этаж лотка или короба равна этажу помещения
                if doc.GetElement(el.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name == room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString():
                    if room.IsPointInRoom(LinkTransform.OfPoint(el.Location.Curve.GetEndPoint(0))) or room.IsPointInRoom(LinkTransform.OfPoint(el.Location.Curve.GetEndPoint(1))):
                        if RoomName:
                            el.LookupParameter('BDV_E000_Имя помещения').Set(RoomName)
                        if FlatNumber:
                            el.LookupParameter('БУДОВА_Номер квартиры').Set(FlatNumber)
                        if RoomNumber:
                            el.LookupParameter('BDV_E000_Номер помещения').Set(RoomNumber)

            # ПОЛЬЗОВАТЕЛЬСКИЕ СЕМЕЙСТВА, СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ КОРОБОВ И КАБЕЛЬНЫХ ЛОТКОВ
            if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Номер квартиры'):
                # если не полоса заземления, категория пожарная сигнализация
                if el.Category.Id.IntegerValue != -2008085:
                    # соединительные детали кабельных лотков и соединительные детали коробов тоже здесь
                    # если семейство не вложенное
                    if el.SuperComponent is None:
                        if room.IsPointInRoom(LinkTransform.OfPoint(el.Location.Point)):
                            if RoomName:
                                el.LookupParameter('BDV_E000_Имя помещения').Set(RoomName)
                            if FlatNumber:
                                el.LookupParameter('БУДОВА_Номер квартиры').Set(FlatNumber)
                            if RoomNumber:
                                el.LookupParameter('BDV_E000_Номер помещения').Set(RoomNumber)

            # ЭЛЕКТРИЧЕСКИЕ ЦЕПИ
            if isinstance(el, DB.Electrical.ElectricalSystem):
                baseEquip = el.BaseEquipment
                # если цепь подключена, иначе у None нет атрибута Host
                if baseEquip:
                    # если уровень панели, к которой подключена цепь равен уровню помещения
                    if baseEquip.Host.Name == room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString():
                        if room.IsPointInRoom(LinkTransform.OfPoint(baseEquip.Location.Point)):
                            if RoomName:
                                el.LookupParameter('BDV_E000_Имя помещения').Set(RoomName)
                            if FlatNumber:
                                el.LookupParameter('БУДОВА_Номер квартиры').Set(FlatNumber)
                            if RoomNumber:
                                el.LookupParameter('BDV_E000_Номер помещения').Set(RoomNumber)


    t.Commit()








































# with DB.Transaction(doc, 'CreateCircuitStoyak') as t:
#     t.Start()
#     for element in FEC(doc, doc.ActiveView.Id).WhereElementIsNotElementType().ToElements():
#         if isinstance(element, DB.FamilyInstance):
#             if element.Symbol.Family.Id == elementIdFamily and "гр" in element.Name:
                # if "гр.4А.15" in element.Name:
                #     con = [connector for connector in element.MEPModel.ConnectorManager.Connectors 
                #             if connector.Domain == DB.Domain.DomainElectrical][0]
                #     circuit = DB.Electrical.ElectricalSystem.Create(con, con.ElectricalSystemType)
                #     circuit.SelectPanel(doc.GetElement(DB.ElementId(6136741)))
    # t.Commit()



#             if "гр.4А.15" in element.Name or "гр.4А.14" in element.Name:
#             # if "ЩЭ8.2.15" in element.Name or "ЩЭ8.2.14" in element.Name:
#                 for connector in element.MEPModel.ConnectorManager.Connectors:
# #                 #     if connector.Domain == DB.Domain.DomainElectrical:
# #                 # for connector in element.MEPModel.ConnectorManager.UnusedConnectors:
# #                         # if element.Name not in dictConnectors:
# #                         #     dictConnectors[element.Name] = []
# #                         # dictConnectors[element.Name].append(connector)
# #                         # dictConnectors[element.Name].append(connector.Owner)
# #                         # dictConnectors[element.Name].append(connector.ConnectorType)

# #                     # if element.Name not in dictConnectors:
# #                     #     dictConnectors[element.Name] = []
# #                     # if connector.Domain == DB.Domain.DomainUndefined:
# #                     #     dictConnectors[element.Name].append(connector)
# #                     #     dictConnectors[element.Name].append(connector.Owner)
# #                     #     dictConnectors[element.Name].append(connector.ConnectorType)
# #                     #     dictConnectors[element.Name].append(connector.Id)

#                     if element.Name not in dictConnectors:
#                         dictConnectors[element.Name] = []
#                     listRef = [con for con in connector.AllRefs]
#                     for conRef in listRef:
#                         dictConnectors[element.Name].append(conRef)
#                         dictConnectors[element.Name].append(conRef.Owner)
#                         # dictConnectors[element.Name].append(conRef.Owner.BaseEquipment)
#                         dictConnectors[element.Name].append(conRef.ConnectorType)
#                         dictConnectors[element.Name].append(conRef.Id)





# # -*- coding: utf-8 -*-
# import clr
# clr.AddReference('RevitAPI')
# from Autodesk.Revit import DB


# class ConnectorsEquipment(object):
#     koef_circuit = 1.05  # коэффициент запаса
#     def __init__(self, equipment):
#         self.equipment = equipment

# isConnected - он подключен
# toConnected - к нему подключен

    #     self.elementId_circuit = self.get_elementId_circuit()
    #     self.voltage = self.get_voltage()
    #     self.cosf = self.get_cosf()
    #     self.active_power = self.get_active_power()
    #     self.length_up_round = self.get_length_up_round()
    #     self.kilovatt_on_meter = self.get_kilovatt_on_meter()
    #     self.dU = self.get_dU()

    # def get_elementId_circuit(self):
    #     return self.circuit.Id

    # def get_voltage(self):
    #     '''напряжение цепи в вольтах'''
    #     parameter = self.circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_VOLTAGE]
    #     unit = parameter.GetUnitTypeId()
    #     return DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)
