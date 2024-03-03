# module select_connectors.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC

from create_circuit_stoyak_floor_shield.user_warning_create_circuit_stoyak_floor_shield import ErrorEmptyParamGroup,\
                                                                                            ErrorEmptyStyleConduit


class SelectConnectors(object):
    def __init__(self, doc, elementIdFamily, panelСonnection):
        self._doc = doc
        self._elementIdFamily = elementIdFamily
        self._panelСonnection = panelСonnection
        self.shieldsInActiveView = self.get_shieldsInActiveView()
        self.shieldSortLevel = self.get_shieldSortLevel()
        self.allConCondAndFit = self.get_allConCondAndFit()
        self.endConnectors = self.get_endConnectors()

    def get_shieldsInActiveView(self):
        dictShields = {}
        # Все что не видно на виде, не попадет в выборку
        for element in FEC(self._doc, self._doc.ActiveView.Id).WhereElementIsNotElementType().ToElements():
            if isinstance(element, DB.FamilyInstance):
                if element.Symbol.Family.Id in self._elementIdFamily:
                    ShieldName = element.Name[:element.Name.rfind('.')]
                    if ShieldName not in dictShields:
                        dictShields[ShieldName] = []
                    dictShields[element.Name[:element.Name.rfind('.')]].append(element)

        return dictShields

    def get_shieldSortLevel(self):
        # Сортируем списки в словаре в порядке убывания высоты уровня, от верхнего к нижнему
        # у верхнего индекс 0 в списке
        shieldSortLevel = {}
        for name_group_str, list_shield in self.shieldsInActiveView.items():
            shieldSortLevel[name_group_str] = sorted(
                    list_shield, key=lambda shield: shield.Host.Elevation, reverse=True)
        return shieldSortLevel

    def get_allConCondAndFit(self):
        '''все коннекторы коробов и соедин.деталей только для щитов попадающих в разрез'''
        allConCondAndFit = {}
        for key in self.shieldsInActiveView.keys():
            allConCondAndFit[key] = []

        for cond in FEC(self._doc).OfCategory(
                    DB.BuiltInCategory.OST_Conduit).WhereElementIsNotElementType().ToElements():
            paramGroup = cond.LookupParameter('БУДОВА_Группа')
            levCond = self._doc.GetElement(cond.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name
            if not paramGroup.AsString():
                raise ErrorEmptyParamGroup(cond, levCond, cond.Id)
            # если параметр заполнен
            if paramGroup:
                if paramGroup.AsString() in allConCondAndFit:
                    # чтоб не попадали вертикальные пластиковые трубы, у них та же самая 'БУДОВА_Группа'
                    paramStyleConduit = self._doc.GetElement(cond.LookupParameter('Стиль коробов').AsElementId())
                    # если параметр не заполнен
                    if not paramStyleConduit or paramStyleConduit is None:
                        raise ErrorEmptyStyleConduit(cond, levCond, cond.Id)
                    if paramStyleConduit:
                        if "гофра" in paramStyleConduit.Name:
                            for connector in cond.ConnectorManager.Connectors:
                                allConCondAndFit[paramGroup.AsString()].append(connector)

        for condFit in FEC(self._doc).OfCategory(
            DB.BuiltInCategory.OST_ConduitFitting).WhereElementIsNotElementType().ToElements():
            paramGroupFit = condFit.LookupParameter('БУДОВА_Группа').AsString()
            if not paramGroupFit:
                levCondFit = self._doc.GetElement(condFit.Parameter[DB.BuiltInParameter.FAMILY_LEVEL_PARAM].AsElementId()).Name
                raise ErrorEmptyParamGroup(condFit, levCondFit, condFit.Id)
            if paramGroupFit in allConCondAndFit:
                for connect in condFit.MEPModel.ConnectorManager.Connectors:
                    allConCondAndFit[paramGroupFit].append(connect)

        return allConCondAndFit

    def get_endConnectors(self):
        '''коннекторы, которые ни к чему не подключены, конечные, 
        ближайшие к панели к которой подключаем цепи'''
        # БЛИЖАЙШИЙ К ЩИТУ КОННЕКТОР не обязательно последний потому находим не соединенный
        endConnectors = {}
        # расположение панели на плоскости XY к которой подключаем цепи
        panelPlaneXyz = DB.XYZ(self._panelСonnection.Location.Point.X, self._panelСonnection.Location.Point.Y, 0)
        for nameGr, listConnectors in self.allConCondAndFit.items():
            endConnectors[nameGr] = []
            # коннектор короба или соед детали от щита не более 3 метров (10 футов) в плоскости XY
            for conPlan in listConnectors:
                if panelPlaneXyz.DistanceTo(
                    DB.XYZ(conPlan.CoordinateSystem.Origin.X, conPlan.CoordinateSystem.Origin.Y, 0)) < 10:
                    # отбираем конечные коннекторы - ни с чем не соединены
                    if not conPlan.IsConnected:
                        endConnectors[nameGr].append(conPlan)

        return endConnectors
