# -*- coding: utf-8 -*
# module rename_circuit.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
# from System.Collections.Generic import List
# import json

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

from create_circuit_stoyak.user_form_create_circuit_stoyak import UserFormCreateCircuitStoyak
from create_circuit_stoyak.user_warning_create_circuit_stoyak import ErrorActiveView,\
                                                    ErrorSizeSectionView,\
                                                    ErrorCancelButton, ErrorNotIsPanelСonnection, ErrorUserNoSelect
from create_circuit_stoyak.user_form_select_link_create_circuit_stoyak import UserFormSelectLinkInstance

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo

userForm = UserFormCreateCircuitStoyak()
userForm.ShowDialog()

if not isinstance(doc.ActiveView, DB.ViewSection):
    raise ErrorActiveView()

if userForm.dictUserSelect["cancelScript"]:
    raise ErrorCancelButton()



unitLengType = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
unitAreaType = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Area).GetUnitTypeId()

with DB.Transaction(doc, 'CreateCircuitStoyak') as t:
    t.Start()
    # Устанавливаем смещение траектории цепи (Управление-НастройкиМЕР-НастройкиЭлектротехническихСистем-Общие)
    doc.Settings.ElectricalSetting.CircuitPathOffset = DB.UnitUtils.ConvertToInternalUnits(
                        0, # смещение в миллиметрах
                        unitLengType
                        )

    # elementId семейства отбираемого на виде разреза (BDV_E000_Коробка ответвительная доза_220в)
    elementIdFamily = [family.Id for family in FEC(doc).OfClass(DB.Family)
                                    if "доза" in family.Name][0]

    # Все что не видно на виде, не попадет в выборку

    dictChifGroup = {}
    # Все что не видно на виде, не попадет в выборку
    for element in FEC(doc, doc.ActiveView.Id).WhereElementIsNotElementType().ToElements():
        if isinstance(element, DB.FamilyInstance):
            if element.Symbol.Family.Id == elementIdFamily:
                dozaPanelName = element.Name[:element.Name.rfind('.')]
                if dozaPanelName not in dictChifGroup:
                    dictChifGroup[dozaPanelName] = []
                dictChifGroup[element.Name[:element.Name.rfind('.')]].append(element)

    # Сортируем списки в словаре в порядке убывания высоты уровня, от верхнего к нижнему
    # у верхнего индекс 0 в списке
    conSortLevel = {}
    for name_group_str, list_doz in dictChifGroup.items():
        conSortLevel[name_group_str] = sorted(list_doz, key=lambda doza: doza.Host.Elevation, reverse=True)

    OUT = []
    for name_group, sort_list_doz in conSortLevel.items():
        for i in range(len(sort_list_doz) - 1):
            # # что подключить
            # sort_list_doz[i]
            # # к чему подключить
            # sort_list_doz[i+1]
            con = [connector for connector in sort_list_doz[i].MEPModel.ConnectorManager.Connectors 
                    if connector.Domain == DB.Domain.DomainElectrical][0]
            # Если реальный коннектор имеет ссылку = есть питающая линия
            # тогда пропускаем одну итерацию
            if [conctr for conctr in con.AllRefs]:
                continue
            listIdLoads = []
            for connecr in sort_list_doz[i].MEPModel.ConnectorManager.Connectors:
                if connecr.Domain == DB.Domain.DomainUndefined:
                    listRef = [conntr for conntr in connecr.AllRefs]
                    for conRef in connecr.AllRefs:
                        for faminst in conRef.Owner.Elements:
                            listIdLoads.append(faminst.Id)
            # Если в списке нагрузок панели есть панель, к которой будем подключать новую цепь
            # (получится циклическая ссылка)
            if sort_list_doz[i+1].Id in listIdLoads:
                raise ErrorSizeSectionView(sort_list_doz[i+1], sort_list_doz[i+1].Id)

            circuit = DB.Electrical.ElectricalSystem.Create(con, con.ElectricalSystemType)
            circuit.SelectPanel(sort_list_doz[i+1])
            OUT.append(circuit.Id)


    # ПОДКЛЮЧЕНИЕ К ВРУ
    if userForm.dictUserSelect["connectToVRY"]:
        # СМЕЩЕНИЕ ТРАЕКТОРИИ ДЛЯ ПОДКЛЮЧЕНИЯ К ВРУ


        # если RevitLinkInstance есть, но GetLinkDocument() равна нулю (LinkInstan.GetLinkDocument() is None),
        # то связь нужно через правую кнопку мыши Обновить
        listLinkInstanceName = [LinkInstan.GetLinkDocument().Title for LinkInstan in FEC(doc).OfClass(DB.RevitLinkInstance) if LinkInstan.GetLinkDocument()]
        userFormSelectLinkInstance = UserFormSelectLinkInstance(listLinkInstanceName)
        userFormSelectLinkInstance.ShowDialog()

        # ЕСЛИ ПОЛЬЗОВАТЕЛЬ НИЧЕГО НЕ ВЫБРАЛ
        if not userFormSelectLinkInstance.listUserSelect:
            raise ErrorUserNoSelect()

        # экземпляр связи
        LinkInstance = [LinkInstan for LinkInstan in FEC(doc).OfClass(DB.RevitLinkInstance) if userFormSelectLinkInstance.listUserSelect[0] in LinkInstan.Name][0]
        # документ связи
        LinkDoc = LinkInstance.GetLinkDocument()
        # # типоразмер связи
        # LinkType = doc.GetElement(LinkInstance.GetTypeId())
        # трансформация из связи
        LinkTransform = LinkInstance.GetTotalTransform()
        # OUT.append(LinkDoc.Title)


        # ВЫБОР ИМЕНИ ПАНЕЛИ УКАЗАННОЙ ПОЛЬЗОВАТЕЛЕМ
        panelСonnection = 0
        for element in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
            if element.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString():
                if userForm.dictUserSelect["objectInVRY"] in element.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString():
                    panelСonnection = element
        # если выбранное пользователем имя панели отстутствует в проекте (электрощитовой)
        if panelСonnection == 0:
            raise ErrorNotIsPanelСonnection(userForm.dictUserSelect["objectInVRY"])

        LevElevatLink = sorted(round(level.Elevation, 3) for level in FEC(LinkDoc).OfClass(DB.Level))
        levelIndexPanelLevel = LevElevatLink.index(round(panelСonnection.Host.Elevation, 3))
        levelIndexAbovePanelLevel = levelIndexPanelLevel + 1
        LevLink = sorted([level for level in FEC(LinkDoc).OfClass(DB.Level)], key=lambda level: level.Elevation)
        listTwoLevelId = [LevLink[levelIndexPanelLevel].Id, LevLink[levelIndexAbovePanelLevel].Id]

        listFloor =[]
        for floor in FEC(LinkDoc).OfClass(DB.Floor):
            # Перекрытия могут быть привязаны по двум разным вариантам:
            # 1. Со смещением от привязанного уровня -100мм, ниже пола
            # 2. Со смещением от привязанного уровня 2900мм, под потолком
            # потому рассматривается два уровня в listTwoLevelId
            if floor.LevelId in listTwoLevelId:
                if all([
                    "Пол" not in floor.Name,
                    "Потолок" not in floor.Name,
                    "Кровля" not in floor.Name,
                    "Фундамент" not in floor.Name
                ]):

                    # если смещение перекрытия 2900мм, под потолком
                    if floor.LevelId == listTwoLevelId[0]:
                        # смещение больше 1000мм
                        # чтоб не входил вариант, когда плита привязана ниже пола
                        if DB.UnitUtils.ConvertFromInternalUnits(
                            floor.Parameter[DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM].AsDouble(), unitLengType) > 1000:
                                listFloor.append(floor)
                    # если смещение перекрытия -100мм, ниже пола
                    if floor.LevelId == listTwoLevelId[1]:
                        # смещение меньше нуля
                        # чтоб не входил вариант, когда плита привязана под потолком
                        if DB.UnitUtils.ConvertFromInternalUnits(
                            floor.Parameter[DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM].AsDouble(), unitLengType) < 0:
                            listFloor.append(floor)

        # перекрытие с максимальной площадью
        FloorMaxArea = sorted(listFloor, key=lambda flo: flo.Parameter[DB.BuiltInParameter.HOST_AREA_COMPUTED].AsDouble(), reverse=True)[0]
        # толщина перекрытия с максимальной площадью
        thickness = FloorMaxArea.Parameter[DB.BuiltInParameter.FLOOR_ATTR_THICKNESS_PARAM].AsDouble()
        offset = 0
        # если смещение перекрытия с максимальной площадью 2900мм, под потолком
        if FloorMaxArea.LevelId == listTwoLevelId[0]:
            # расстояние между двумя уровнями минус смещение плиты, которое всегда положительное по условию
            offset = -1 * ((LinkDoc.GetElement(listTwoLevelId[1]).Elevation - LinkDoc.GetElement(listTwoLevelId[0]).Elevation) \
                                - FloorMaxArea.Parameter[DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM].AsDouble())
        # смещение перекрытия с максимальной площадью -100мм, ниже пола
        if FloorMaxArea.LevelId == listTwoLevelId[1]:
            # модуль от смещения, которое всегда отрицательное по условию
            offset = FloorMaxArea.Parameter[DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM].AsDouble()

        # смещение кабельного лотка от потолка, учитывая толщину кабеля 190мм
        offsetCableTray = DB.UnitUtils.ConvertToInternalUnits(190, unitLengType)
        # смещение ниже уровня с учетом толщины плиты и кабельного лотка(200мм - диаметр кабеля = 190мм)
        # -100(offset) - 220(thickness) - 190(offsetCableTray)
        belowLevel = offset - thickness - offsetCableTray

        # отметка уровня над уровнем точки подключений
        elevatAboveLevel = LevElevatLink[levelIndexAbovePanelLevel]

        # ПОДКЛЮЧАЕМ ЦЕПИ К ВРУ
        # Если подключения к ВРУ не нужно делать, то эту часть скрипта не выполняем
        for name_group, sort_list_doz in conSortLevel.items():
            # # чтобы подключить(последний элемент списка) = sort_list_doz[-1]
            # к чему подключить(точка подключений ВРУ) = panelСonnection
            conctor = [connctor for connctor in sort_list_doz[-1].MEPModel.ConnectorManager.Connectors 
                    if connctor.Domain == DB.Domain.DomainElectrical][0]
            # Если реальный коннектор имеет ссылку = есть питающая линия
            if [conn for conn in conctor.AllRefs]:
                # тогда пропускаем одну итерацию
                continue

            # Устанавливаем смещение траектории цепи (Управление-НастройкиМЕР-НастройкиЭлектротехническихСистем-Общие)
            # высчитывается в зависимости от этажа коробки и этажа точки подключений, с учетом расположения плиты 1го этажа
            # смещение во внутренних единицах (belowLevel со знаком (-) минус потому + не ошибка)
            doc.Settings.ElectricalSetting.CircuitPathOffset = elevatAboveLevel - round(sort_list_doz[-1].Host.Elevation, 3) + belowLevel
            circuit = DB.Electrical.ElectricalSystem.Create(conctor, conctor.ElectricalSystemType)
            circuit.SelectPanel(panelСonnection)
            OUT.append(circuit.Id)

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
