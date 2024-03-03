# module path_for_circuit.py
# -*- coding: utf-8 -*-
# Первый узел = location панели
# Последний узел = координаты 1 из 5 коннекторов щита
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List


class PathForCircuit(object):
    def __init__(self, currentShield, currentCon, conPanel, endCon):
        self._currentShield = currentShield  # текущий щит
        self._currentCon = currentCon  # один из 5 коннекторов щита
        self._conPanel = conPanel  # коннектор панели к которой подключаем, указанной пользователем
        self._firstCon = endCon  # конечный коннектор для текущего щита
        self.path = self.get_path()

    def get_path(self):
        '''УЗЛЫ ПУТИ'''
        listPath = List[DB.XYZ]()

        # ПЕРВЫЙ УЗЕЛ = xyz коннектора панели, к которой подключаем conPanel.Domain == DB.Domain.DomainElectrical
        # Location.Point панели и положения коннектора не одно и тоже, пробуем положение конектора.
        node1 = self._conPanel.Owner.Location.Point
        listPath.Add(node1)

        # ВТОРОЙ УЗЕЛ = под коннектором панели на высоте осевой линии короба
        #  И ТРЕТИЙ УЗЕЛ = проекция второго узла на осевую линию короа
        if isinstance(self._firstCon.Owner, DB.Electrical.Conduit):
            # не каждый ближайший до панели элемент является коробом
            # boundLine.Origin.Z = десятичное число с 13 или 14 знаков после
            # запятой, по разному - могут быть неточности

            # осевая линия короба
            boundLineС = self._firstCon.Owner.Location.Curve
            unboundLineС = DB.Line.CreateUnbound(boundLineС.Origin, boundLineС.Direction)
            node2 = DB.XYZ(0,0,0)
            # Z меньше плюс-минус 1мм, короб лежит в плоскости XY
            # ЕСЛИ ГОРИЗОНТАЛЬНЫЙ КОРОБ СОВМЕЩАЕМ ПО ОСИ Z в node2
            # если короб идет горизонтально, то Z = 0 (с отклонениями в 10 знаке после запятой)
            if abs(self._firstCon.Owner.Location.Curve.Direction.Z) < 0.003:
                # ВТОРОЙ УЗЕЛ над точкой размещения панели на уровне осевой линии короба
                node2 = DB.XYZ(node1.X, node1.Y, boundLineС.Origin.Z)
            # ЕСЛИ ВЕРТИКАЛЬНОЫЙ КОРОБ СОВМЕЩАЕМ ПО ОСИ Х в node2
            # если короб идет вниз, то Z = -1, вверх Z = 1
            if abs(self._firstCon.Owner.Location.Curve.Direction.Z) > 0.997:
                # ВТОРОЙ УЗЕЛ напротив размещения панели на уровне осевой линии короба по оси X
                node2 = DB.XYZ(boundLineС.Origin.X, node1.Y, node1.Z)
            # ТРЕТИЙ УЗЕЛ = xyz проекции на ось короба
            node3 = unboundLineС.Project(node2).XYZPoint
            listPath.Add(node2)
            listPath.Add(node3)
            # коннектор протвиположного конца короба
            nextCon = [conc for conc in self._firstCon.Owner.ConnectorManager.Connectors 
                            if conc.Id != self._firstCon.Id and conc.ConnectorType == DB.ConnectorType.End][0]
            # этот коннектор уже соед.детали и в следующем ифе он уже будет обрабатываться
            startCon = [sCon for sCon in nextCon.AllRefs if nextCon.Owner.Id != sCon.Owner.Id][0]

        # если ближайший к щиту это коннектор сеод.детали, то переходим к подключенному к нему
        # коробу и получаем точку пересечения с осью короба
        if self._firstCon.Owner.Category.Id == DB.ElementId(DB.BuiltInCategory.OST_ConduitFitting):
            nextCon = [concf for concf in self._firstCon.Owner.MEPModel.ConnectorManager.Connectors 
                            if concf.Id != self._firstCon.Id and concf.ConnectorType == DB.ConnectorType.End][0]
            # это коннектор уже короба
            conduitCon = [conC for conC in nextCon.AllRefs][0]
            boundLine = conduitCon.Owner.Location.Curve
            unboundLine = DB.Line.CreateUnbound(boundLine.Origin, boundLine.Direction)
            # ВТОРОЙ УЗЕЛ под коннектором щита на уровне осевой линии короба
            node2 = DB.XYZ(node1.X, node1.Y, boundLine.Origin.Z)
            listPath.Add(node2)
            # ТРЕТИЙ УЗЕЛ = xyz проекции на ось короба
            node3 = unboundLine.Project(node2).XYZPoint
            listPath.Add(node3)

            # получаем коннектор этого же короба для продолжения обхода
            startCon = [sConf for sConf in nextCon.AllRefs][0]

        # цикл повторяется пока выполняется условие = коннектор подключен
        while startCon.IsConnected:

            if isinstance(startCon.Owner, DB.Electrical.Conduit):
                nextCon = [concw for concw in startCon.Owner.ConnectorManager.Connectors 
                                if concw.Id != startCon.Id and concw.ConnectorType == DB.ConnectorType.End][0]
                if nextCon.IsConnected:
                    startCon = [nCon for nCon in nextCon.AllRefs 
                                if nextCon.Owner.Id != nCon.Owner.Id][0]
                else:
                    # подключаем к одному из 5 коннекторов щита
                    nodeEndPath = self._currentCon.CoordinateSystem.Origin
                    # осевая линия короба
                    boundLineС = nextCon.Owner.Location.Curve
                    unboundLineС = DB.Line.CreateUnbound(boundLineС.Origin, boundLineС.Direction)
                    # Z меньше плюс-минус 1мм, короб лежит в плоскости XY
                    # если короб идет вниз, то Z = -1
                    # ГОРИЗОНТАЛЬНЫЙ КОРОБ
                    if abs(nextCon.Owner.Location.Curve.Direction.Z) < 0.003:
                        # ПРЕДПОСЛЕДНИЙ(-2) УЗЕЛ над точкой размещения панели на уровне осевой линии короба
                        node_2 = DB.XYZ(nodeEndPath.X, nodeEndPath.Y, boundLineС.Origin.Z)
                    # ЕСЛИ ВЕРТИКАЛЬНОЫЙ КОРОБ СОВМЕЩАЕМ ПО ОСИ Х в node_2
                    # если короб идет вниз, то Z = -1, вверх Z = 1
                    if abs(nextCon.Owner.Location.Curve.Direction.Z) > 0.997:
                        # ПРЕДПОСЛЕДНИЙ(-2) УЗЕЛ напротив размещения панели на уровне осевой линии короба по оси X
                        node_2 = DB.XYZ(boundLineС.Origin.X, nodeEndPath.Y, nodeEndPath.Z)
                    # ПРЕДПРЕДПОСЛЕДНИЙ(-3) УЗЕЛ = xyz проекции на ось короба
                    node_3 = unboundLineС.Project(node_2).XYZPoint
                    listPath.Add(node_3)
                    listPath.Add(node_2)
                    listPath.Add(nodeEndPath)
                    startCon = nextCon

            if startCon.Owner.Category.Id == DB.ElementId(DB.BuiltInCategory.OST_ConduitFitting):
                nextCon = [conf for conf in startCon.Owner.MEPModel.ConnectorManager.Connectors 
                                if conf.Id != startCon.Id and conf.ConnectorType == DB.ConnectorType.End][0]
                if nextCon.IsConnected:
                    # ДОБАВЛЯЕМ В ПУТЬ УЗЕЛ КАК xyz точки размещения соед.детали
                    # так как она является пересечением осевых линий коробов
                    listPath.Add(startCon.Owner.Location.Point)
                    startCon = [nConf for nConf in nextCon.AllRefs][0]
                else:
                    # startCon получили как раз с педыдущего короба
                    conConduit = [prevCon for prevCon in startCon.AllRefs][0]  # коннектор короба
                    # подключаем к одному из 5 коннекторов щита
                    nodeEndPath = self._currentCon.CoordinateSystem.Origin
                    # осевая линия короба
                    boundLineС = conConduit.Owner.Location.Curve
                    unboundLineС = DB.Line.CreateUnbound(boundLineС.Origin, boundLineС.Direction)
                    node_2 = DB.XYZ(0,0,0)
                    # Z меньше плюс-минус 1мм, короб лежит в плоскости XY
                    # ЕСЛИ ГОРИЗОНТАЛЬНЫЙ КОРОБ СОВМЕЩАЕМ ПО ОСИ Z в node_2
                    # если короб идет горизонтально, то Z = 0 (с отклонениями в 10 знаке после запятой)
                    if abs(conConduit.Owner.Location.Curve.Direction.Z) < 0.003:
                        # ПРЕДПОСЛЕДНИЙ(-2) УЗЕЛ над точкой размещения панели на уровне осевой линии короба
                        node_2 = DB.XYZ(nodeEndPath.X, nodeEndPath.Y, boundLineС.Origin.Z)
                    # ЕСЛИ ВЕРТИКАЛЬНОЫЙ КОРОБ СОВМЕЩАЕМ ПО ОСИ Х в node_2
                    # если короб идет вниз, то Z = -1, вверх Z = 1
                    if abs(conConduit.Owner.Location.Curve.Direction.Z) > 0.997:
                        # ПРЕДПОСЛЕДНИЙ(-2) УЗЕЛ напротив размещения панели на уровне осевой линии короба по оси X
                        node_2 = DB.XYZ(boundLineС.Origin.X, nodeEndPath.Y, nodeEndPath.Z)
                    # ПРЕДПРЕДПОСЛЕДНИЙ(-3) УЗЕЛ = xyz проекции на ось короба
                    node_3 = unboundLineС.Project(node_2).XYZPoint
                    listPath.Add(node_3)
                    listPath.Add(node_2)
                    listPath.Add(nodeEndPath)
                    startCon = nextCon
        return listPath



























    def get_shieldsInActiveView(self):
        dictShields = {}
        # Все что не видно на виде, не попадет в выборку
        for element in FEC(self._doc, self._doc.ActiveView.Id).WhereElementIsNotElementType().ToElements():
            if isinstance(element, DB.FamilyInstance):
                if element.Symbol.Family.Id in self._elementIdFamily:
                    ShieldName = element.Name[:element.Name.rfind('.')]
                    if ShieldName not in dictShields:
                        dictShields[ShieldName] = []
                    dictShields[element.Name[:element.Name.rfind('.')]].Add(element)

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
                                allConCondAndFit[paramGroup.AsString()].Add(connector)

        for condFit in FEC(self._doc).OfCategory(
            DB.BuiltInCategory.OST_ConduitFitting).WhereElementIsNotElementType().ToElements():
            paramGroupFit = condFit.LookupParameter('БУДОВА_Группа').AsString()
            if not paramGroupFit:
                levCondFit = self._doc.GetElement(condFit.Parameter[DB.BuiltInParameter.FAMILY_LEVEL_PARAM].AsElementId()).Name
                raise ErrorEmptyParamGroup(condFit, levCondFit, condFit.Id)
            if paramGroupFit in allConCondAndFit:
                for connect in condFit.MEPModel.ConnectorManager.Connectors:
                    allConCondAndFit[paramGroupFit].Add(connect)

        return allConCondAndFit

    def get_endConnectors(self):
        '''коннекторы, которые ни к чему не подключены, конечные, ближайшие к щиту'''
        # БЛИЖАЙШИЙ К ЩИТУ КОННЕКТОР не обязательно последний потому находим не соединенный
        endConnectors = {}
        # Находим ближайший до щита соединитель в плоскости X,Y
        for nameGroup, listShields in self.shieldSortLevel.items():
            # расположение первого щита из списка на плоскости XY
            shieldPlaneXyz = DB.XYZ(listShields[0].Location.Point.X, listShields[0].Location.Point.Y, 0)
            for nameGr, listConnectors in self.allConCondAndFit.items():
                endConnectors[nameGr] = []
                # коннектор короба или соед детали от щита не более 1,5 метров (5 футов) в плоскости XY
                for conPlan in listConnectors:
                    if shieldPlaneXyz.DistanceTo(
                        DB.XYZ(conPlan.CoordinateSystem.Origin.X, conPlan.CoordinateSystem.Origin.Y, 0)) < 5:
                        # отбираем конечные коннекторы - ни с чем не соединены
                        if not conPlan.IsConnected:
                            endConnectors[nameGr].Add(conPlan)

        return endConnectors
