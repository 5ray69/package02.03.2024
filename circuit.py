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

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo


# # СДЕЛАТЬ ПРЕДУПРЕЖДЕНИЕ, ЧТО ВИД НЕ РАЗРЕЗ
# # если активный вид - это разрез
# if isinstance(doc.ActiveView, DB.ViewSection):
#     OUT = True
# else:
#     OUT = "активный вид это не разрез"

    # имя семейства "BDV_E000_Коробка ответвительная доза":
elementIdFamily = [family.Id for family in FEC(doc).OfClass(DB.Family)
                                if "доза" in family.Name][0]

# OUT = []
# for element in FEC(doc, doc.ActiveView.Id).WhereElementIsNotElementType().ToElements():
#     if isinstance(element, DB.FamilyInstance):
#         if element.Symbol.Family.Id == elementIdFamily and "гр" in element.Name:
#             OUT.append(element.Name)

OUT = []
dictConnectors = {}
dictUnusedConnectors = {}
for element in FEC(doc, doc.ActiveView.Id).WhereElementIsNotElementType().ToElements():
    if isinstance(element, DB.FamilyInstance):
        if element.Symbol.Family.Id == elementIdFamily and "гр" in element.Name:
            if element.Name not in dictConnectors:
                dictConnectors[element.Name] = []
            # for connector in element.MEPModel.ConnectorManager.Connectors:
            #     # если цепь не подсоедина, то коннектор один

            #     # если к дозе подсоединена цепь, то становится два коннектора:
            #     # один свободный, для подсоединения коробки к чему-то,
            #     # а другой занятый, имеющий ссылку на цепь, которая подсоедина к коробке/коннектору
            #     dictConnectors[element.Name].append(connector.Id)
            #     dictConnectors[element.Name].append(connector.Domain)



            # # Неиспользованные коннекторы - это реальные, не виртуальные коннекторы.
            # # Это не значит, что к ним ничего не подключено
            # # и это не значит, что они ни чему не подключены
            # for con in element.MEPModel.ConnectorManager.UnusedConnectors:
            #     dictConnectors[element.Name].append(con)
            #     dictConnectors[element.Name].append(con.IsConnected)
            #     dictConnectors[element.Name].append(con.Owner)

            # При подключении создаются виртуальные коннекторы
            # Но они создаются как при подключении к коннектору, так и при подключении самого коннектора к другому
            # Виртуальный коннектор всегда ссылается на цепь
            # Как узнать, что виртуальный коннектор подключен, а не к нему подключены?
            # Если извлечь у цепей, на которые ссылаются виртуальные коннекторы .BaseEquipment, то
            # если  коннектору подключение, то .BaseEquipment вернет ту панель, в которой находится реальный коннектор
            # если  коннектор сам подключен к другой панели, то .BaseEquipment вернет другую панель, не ту в которой находится реальный коннектор
            # то есть если .BaseEquipment вернул не ту панель в которой находится, то есть подключение к другой цепи,
            # это и определяет подключен ли коннектор
            dictConnectors[element.Name].append(element)
            for connector in element.MEPModel.ConnectorManager.Connectors:
                reflist = [con for con in connector.AllRefs if con.Domain == DB.Domain.DomainElectrical]
                # reflist = [con.Owner.BaseEquipment for con in connector.AllRefs]
                # if not reflist:
                #     listConnectors.append(connector.Owner)
                if reflist:
                    # Owner подключенного сединителя - это ElectricalSystem (цепь)
                    dictConnectors[element.Name].append(reflist)
OUT = dictConnectors

# Пусть у FamilyInstanc-а есть один электрический коннектор в семействе.
# Если к FamilyInstanc-у подключить цепь, то у него пявлется виртуальный коннектор, 
# итого становится 2 коннектора: реальный и виртуальный. Виртуальный коннектор имеет ссылку AllRefs на цепь (Owner = цепь).
# Сколько подключений к коннектору, столько и виртуальных коннекторов появляется, например, если к коннектору подключено 
# 3 цепи, то появляется три виртуальных коннектора, имеющих ссылки на цепи и существует все тот же 1 реальный коннектор, 
# итого 4 коннектора (1 реальный и 3 виртуальнах)

# реальный (невитруальный) коннектор имеет домен DomainElectrical
# connector.Domain == DB.Domain.DomainElectrical

# виртуальный коннектор с неопределенным доменом появляется, когда к соединителю есть подключение, но сам соединительтоже можно подключить
# connector.Domain == DB.Domain.DomainUndefined

#             if element.Name not in dictUnusedConnectors:
#                 dictUnusedConnectors[element.Name] = []
#             # Неиспользованные коннекторы - это реальные, не виртуальные коннекторы.
#             # Это не значит, что к ним ничего не подключено
#             # и это не значит, что они ни чему не подключены
#             dictUnusedConnectors[element.Name].append([con.AllRefs for con in element.MEPModel.ConnectorManager.UnusedConnectors])
# OUT = dictUnusedConnectors

            # listConnectors = []
            # for connector in element.MEPModel.ConnectorManager.Connectors:
            #     reflist = [con for con in connector.AllRefs]
            #     # if not reflist:
            #     #     listConnectors.append(connector.Owner)
            #     if reflist:
            #         # Owner подключенного сединителя - это ElectricalSystem (цепь)
            #         listConnectors.append(reflist[0].Owner)
            #     # listConnectors.append(connector.AllRefs)
            # OUT.append(listConnectors)



# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


class ConnectorsEquipment(object):
    koef_circuit = 1.05  # коэффициент запаса
    def __init__(self, equipment):
        self.equipment = equipment

# isConnected - он подключен
# toConnected - к нему подключен

        self.elementId_circuit = self.get_elementId_circuit()
        self.voltage = self.get_voltage()
        self.cosf = self.get_cosf()
        self.active_power = self.get_active_power()
        self.length_up_round = self.get_length_up_round()
        self.kilovatt_on_meter = self.get_kilovatt_on_meter()
        self.dU = self.get_dU()

    def get_elementId_circuit(self):
        return self.circuit.Id

    def get_voltage(self):
        '''напряжение цепи в вольтах'''
        parameter = self.circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_VOLTAGE]
        unit = parameter.GetUnitTypeId()
        return DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)




