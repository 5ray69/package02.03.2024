# -*- coding: utf-8 -*
# module create_circuit_stoyak_floor_shield.py
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

from create_circuit_stoyak_floor_shield.select_connectors import SelectConnectors
from create_circuit_stoyak_floor_shield.path_for_circuit import PathForCircuit
from create_circuit_stoyak_floor_shield.user_form_create_circuit_stoyak_floor_shield import UserFormCreateCircuitStoyak
from create_circuit_stoyak_floor_shield.user_warning_create_circuit_stoyak_floor_shield import ErrorActiveView,\
                                                    ErrorCancelButton

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo

# ФОРМА ПОЛЬЗОВАТЕЛЯ
userForm = UserFormCreateCircuitStoyak()
userForm.ShowDialog()
if not isinstance(doc.ActiveView, DB.ViewSection):
    raise ErrorActiveView()
if userForm.dictUserSelect["cancelScript"]:
    raise ErrorCancelButton()

unitLengType = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()  # или  UnitTypeId.Millimeters
unitAreaType = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Area).GetUnitTypeId()  # или  UnitTypeId.SquareMeters


with DB.Transaction(doc, 'CreateCircuitStoyakShield') as t:
    t.Start()
    # ЩИТЫ
    # список elementId семейств этажных щитов
    elementIdFamily = [family.Id for family in FEC(doc).OfClass(DB.Family)
                                    if "Щит этажный" in family.Name or "офисов" in family.Name]

    # ВЫБОР ПАНЕЛИ УКАЗАННОЙ ПОЛЬЗОВАТЕЛЕМ
    panelСonnection = 0
    for element in FEC(doc).OfCategory(
                DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
        if element.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString():
            panelName = element.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
            if userForm.dictUserSelect["objectInVRY"] == panelName[:panelName.rfind('.')]:
            # if "точка подключений" in element.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString():
                panelСonnection = element
    # коннектор панели к которой подключаем
    conPanel = [conp for conp in panelСonnection.MEPModel.ConnectorManager.Connectors 
            if conp.Domain == DB.Domain.DomainElectrical][0]

    selectCon = SelectConnectors(doc, elementIdFamily, panelСonnection)
    shieldSortLevel = selectCon.get_shieldSortLevel()
    # коннекторы, которые не соединены = конечные, самые близкие к панели в плоскости XY
    endConnectors = selectCon.get_endConnectors()

    # Устанавливаем смещение траектории цепи (Управление-НастройкиМЕР-НастройкиЭлектротехническихСистем-Общие)
    doc.Settings.ElectricalSetting.CircuitPathOffset = DB.UnitUtils.ConvertToInternalUnits(
                        0, # смещение в миллиметрах
                        unitLengType
                        )
    # тип системы = мощность
    ElSysType = DB.Electrical.ElectricalSystemType.PowerCircuit

    # ПОСТРОЕНИЕ ЦЕПЕЙ ОТ ЩЭ К ЩЭ
    OUT = []
    # Щиты в словаре в порядке убывания высоты уровня, от верхнего к нижнему (у верхнего индекс 0 в списке)
    for name_group, sort_list_shield in shieldSortLevel.items():
        # если в списке больше одного щита
        if len(sort_list_shield) > 1:
            for i in range(len(sort_list_shield) - 1):
                # # что подключить
                # sort_list_shield[i]
                # # к чему подключить
                # sort_list_shield[i+1]
                # здесь сейчас 5 коннекторов
                list_con = [c for c in sort_list_shield[i].MEPModel.ConnectorManager.Connectors 
                        if c.Domain == DB.Domain.DomainElectrical]
                for currentCon in list_con:
                    # Если реальный коннектор имеет ссылку = есть питающая линия
                    # тогда пропускаем одну итерацию
                    if [conctr for conctr in currentCon.AllRefs]:
                        continue
                    # circuit = DB.Electrical.ElectricalSystem.Create(currentCon, currentCon.ElectricalSystemType)
                    circuit = DB.Electrical.ElectricalSystem.Create(currentCon, ElSysType)
                    circuit.SelectPanel(sort_list_shield[i+1])
                    OUT.append(circuit.Id)

    dictPath = {}
    # ПОСТРОЕНИЕ ЦЕПЕЙ ПОДКЛЮЧЕНИЯ К ВРУ (К ПАНЕЛИ УКАЗАНОЙ ПОЛЬЗОВАТЕЛЕМ)
    # dtValidPath = {}
    # directShape = {}
    for name_group, sort_list_shield in shieldSortLevel.items():
        dictPath[name_group] = []
        # dtValidPath[name_group] = []
        # directShape[name_group] = []
        # что подключить(последний элемент списка) = sort_list_shield[-1]
        # к чему подключить(точка подключений ВРУ) = panelСonnection
        # здесь сейчас 5 коннекторов
        list_con = [connector for connector in sort_list_shield[-1].MEPModel.ConnectorManager.Connectors 
                if connector.Domain == DB.Domain.DomainElectrical]
        for currentCon in list_con:
            # передаем текущий щит (что подключаем)
            # и коннектор панели к которой подключаем
            pathForCon = PathForCircuit(
                sort_list_shield[-1], currentCon, conPanel, endConnectors[name_group][0])
            dictPath[name_group].append(pathForCon.get_path())
            # Если реальный коннектор имеет ссылку = есть питающая линия
            # тогда пропускаем одну итерацию
            if [conctr for conctr in currentCon.AllRefs]:
                continue
            # circuit = DB.Electrical.ElectricalSystem.Create(currentCon, currentCon.ElectricalSystemType)
            circuit = DB.Electrical.ElectricalSystem.Create(currentCon, ElSysType)
            circuit.SelectPanel(panelСonnection)
            # если не регенерировать, то список для примененеия пути цепи будет не валидный
            # видимо цепь еще не создана до окончания транзакции без регенерации
            doc.Regenerate()
            # dtValidPath[name_group].append(circuit.IsCircuitPathValid(pathForCon.get_path()))
            circuit.SetCircuitPath(pathForCon.get_path())

            OUT.append(circuit.Id)

    # directShape = []
    # for xyz in dictPath['ЩЭ1.2'][0]:
    #     i = DB.Point.Create(xyz)
    #     direct_shape = DB.DirectShape.CreateElement(doc, DB.ElementId(DB.BuiltInCategory.OST_GenericModel))
    #     direct_shape.SetShape(List[DB.GeometryObject]([i]))
    #     directShape.append(direct_shape.Id)
    t.Commit()







# Exception: The list of the electrical system circuit path node position is not valid. 
# The length of the list should be more than one, the first node should be the position of the panel 
# where the circuit begins at, the adjacent nodes should not be too close, and should be 
# in the same level or on the same vertical line, to keep each segment of the circuit path always 
# horizontal or vertical. Also note that the first node position 
# should be the position of the connector (the one connects to the circuit) of the panel, 
# but not the origin of the panel instance.
# Parameter name: nodes

# это перевод исключения он ошибочный местами:
# Исключение: Недопустимый список расположения узла тракта цепи электрической системы. 
# Длина списка должна быть больше единицы, первый узел должен быть положением панели, 
# где начинается цепь, соседние узлы не должны быть слишком близки и должны находиться 
# на одном уровне или на одной вертикальной линии, чтобы каждый сегмент пути цепи всегда 
# оставался горизонтальным или вертикальным. Также следует отметить, что первое положение 
# узла должно быть положением соединителя (подключенного к цепи) панели, но не началом 
# координат экземпляра панели.
# имя параметра: узлы



# это реальное описание, оно правильное:
# Нужен типизированный список listPath = List[DB.XYZ]()
# Первый узел (начало цепи) XYZ Location Point семейства (панели) к которому подключена цепь(идекс в списке 0)
# Последний узел (конец цепи) XYZ коннектора в семействе (нагрузки), которое подключено цепью (последний индекс в списке)

# чтоб скрипт работал необходимо лотки располагать или строго горизонтально
#  или строго вертикально, не под наклоном
# короб должен быть предпочтительно горизонтальным, без поворотов вверх или вниз посередине
# окончание короба под щитами:
# заворачивать к щиту вверх короб вертикальным участком короба стиля гофра нельзя! можно оставить окончание только соединительной деталью короба

# окончание короба в помещении ВРУ:
# заворачивать короб вертикальным участком короба стиля гофра вниз, в помещении ВРУ можно!
