# module boundary_intersect_test_room.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
# from Autodesk.Revit.DB import FilteredElementCollector as FEC
# from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа


class BordersRoom(object):
    resultIntersect = clr.Reference[DB.IntersectionResultArray]()

    def __init__(self, room, linkTransform):
        self.room = room
        self.linkTransform = linkTransform
        self.levelZ = self.room.Level.Elevation
        self.BoundarysToCenter = self.getBordersToCenter()

    def getBordersToCenter(self):
        """ЛИНИИ ГРАНИЦ ПОМЕЩЕНИЯ
        на уровне координаты Z уровня помещения
        с учетом трансформации связи"""

        # назначаем переменную на свойство
        roomoptions = DB.SpatialElementBoundaryOptions()
        # установили свойство границы помещения по осевой линии/центру
        roomoptions.SpatialElementBoundaryLocation = DB.SpatialElementBoundaryLocation.Center

        # ГРАНИЦЫ ПОМЕЩЕНИЯ в уровне координаты Z того уровня, к которому привязано помещение
        roomLines = []
        for bound_segments in self.room.GetBoundarySegments(roomoptions):
            for bound_segment in bound_segments:
                lineSegment = bound_segment.GetCurve()

                startPoint = lineSegment.GetEndPoint(0)
                endPoint = lineSegment.GetEndPoint(1)

                roomLines.append(DB.Line.CreateBound(
                    self.linkTransform.OfPoint(DB.XYZ(startPoint.X, startPoint.Y, self.levelZ)),
                    self.linkTransform.OfPoint(DB.XYZ(endPoint.X, endPoint.Y, self.levelZ))
                ))

        return roomLines

    def getXYZVerticesBorders(self):
        """XYZ ВЕРШИН УГЛОВ ГРАНИЦ ПОМЕЩЕНИЯ
        образованы только началами линий
        на уровне координаты Z уровня помещения
        с учетом трансформации связи"""

        verticesRoomLines = []
        for linesBorder in self.bordersToCenter:
            verticesRoomLines.append(self.linkTransform.OfPoint(DB.XYZ(
                linesBorder.GetEndPoint(0).X, linesBorder.GetEndPoint(0).Y, self.levelZ
                )))

        return verticesRoomLines

    def insideTheBorders(self, LocationLine):
        """ВОЗВРАЩАЕТ TRUE ЕСЛИ ПРОЕКЦИЯ ЛИНИИ ПЕРЕСЕКАЕТ ГРАНИЦУ ПОМЕЩЕНИЯ.
        Принимает Line или XYZ (полученые из Location объектов)
        Сколько бы пересечений с границей помещения ни было и где б они ни были,
        то объект в помещении.
        Даже если одна точка/край линии лежит на границе помещения, а вся остальная часть линии вне.
        Если линия совпадает с линией границы помещения, то объект в помещении."""

        # до работы с линией проекции выяснить не вертикальная ли она, ведь тогда проекция будет точкой
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Проекция на уровень координаты Z уровня помещения
        projectLine = DB.Line.CreateBound(
        DB.XYZ(LocationLine.GetEndPoint(0).X, LocationLine.GetEndPoint(0).Y, self.levelZ),
        DB.XYZ(LocationLine.GetEndPoint(1).X, LocationLine.GetEndPoint(1).Y, self.levelZ)
        )

        projectIntersect = {}

        for roomLine in self.BoundarysToCenter:

            # ЕСЛИ ЕСТЬ ЛЮБОЕ НАЛОЖЕНИЕ ПРОЕКЦИИ НА ГРАНИЦУ ПОМЕЩЕНИЯ, ТО ОБЪЕКТ В ПОМЕЩЕНИИ
            # любое наложение - это или наложение точных копий,
            # или наложение линий не равной длины с смещениями относительно начала
            if projectLine.Intersect(roomLine, self.resultIntersect) == DB.SetComparisonResult.Equal:
                return True

            # ЕСЛИ ПРОЕКЦИЯ ЛИНИИ ПЕРЕСЕКАЕТ ГРАНИЦУ ПОМЕЩЕНИЯ, ТО ОБЪЕКТ В ПОМЕЩЕНИИ
            # проекция линии без удлинения нужна прежде удлиненной линии потому, что
            # линия может заходить извне и обрываться в помещении, тогда ее удлинение,
            # даст два пересечения границы помещения, что соотвествует условию
            # нахождения тестовой удлиненной линии вне помещения
            if projectLine.Intersect(roomLine, self.resultIntersect) == DB.SetComparisonResult.Overlap:

                startXYZ = roomLine.GetEndPoint(0)
                sumStartXYZ = str(round(startXYZ.X + startXYZ.Y + startXYZ.Z, 7))
                # Если projectLine проходит через вершину = начальную точку линии границы.
                # Проходя через вершину, линия пересекает две линии границы помещения сразу и дает 2 пересечения.
                # Если такая вершина уже есть в словаре, то второе пересечение ее же,
                # но в другой лини не будет добавлено в словарь и будет зачтено как одно пересечение
                if projectLine.Distance(startXYZ) == 0.0:
                    if sumStartXYZ not in projectIntersect:
                        projectIntersect[sumStartXYZ] = 1

                endXYZ = roomLine.GetEndPoint(1)
                sumEndXYZ = str(round(endXYZ.X + endXYZ.Y + endXYZ.Z, 7))
                # Если projectLine проходит через вершину = начальную точку линии границы.
                if projectLine.Distance(endXYZ) == 0.0:
                    if sumEndXYZ not in projectIntersect:
                        projectIntersect[sumEndXYZ] = 1

                # если projectLine не проходит
                # ни через вершину начальной точки линии границы,
                # ни через вершину конечной точки линии границы (пересекает где-то в другом месте линию границы)
                if projectLine.Distance(startXYZ) != 0.0 and projectLine.Distance(endXYZ) != 0.0:
                    centerLineXYZ = roomLine.Origin
                    currentKey = str(round(centerLineXYZ.X + centerLineXYZ.Y + centerLineXYZ.Z, 7))
                    if currentKey not in projectIntersect:
                        projectIntersect[currentKey] = 1

        # если в словаре насобирали пересечения, то объект в помещении
        if projectIntersect:
            return True

        # иначе словарь пуст, и тогда проверяем удлиненной/тестовой линией
        if not projectIntersect:
            # ЕСЛИ КОРОБ/ПРОЕКЦИЯ ОСЕВЕЙ ЛИНИИ НЕ ПЕРЕСЕКАЕТ ГРАНИЦУ ПОМЕЩЕНИЯ,
            # то он или внутри, или вне границы помещения
            # поэтому из проекции строим удлиненную тестовую линию для проверки пересечений
            # количество пересечений = 0 - вне помещения
            # количество пересечений четное - вне помещения
            # количество пересечений нечетное в помещении

            # ТЕСТОВАЯ ЛИНИЯ
            # задаем в мм, удобно для человека, а код переводит во внутренние единицы
            # длина здания около 60000мм (длинный коридор) потому берем 70000мм
            testLength = DB.UnitUtils.ConvertToInternalUnits(70000, DB.UnitTypeId.Millimeters)

            # первая точка тестовой линии
            testPoint0 = projectLine.GetEndPoint(0)
            # вторая точка тестовой линии
            testPoint1 = projectLine.GetEndPoint(0) + projectLine.Direction.Normalize() * testLength

            # строим тестовую линию в уровне координаты Z того уровня, к которому привязано помещение
            # у помщенеий разных уровней должны быть разные координаты Z
            testLine = DB.Line.CreateBound(
                DB.XYZ(testPoint0.X, testPoint0.Y, self.levelZ),
                DB.XYZ(testPoint1.X, testPoint1.Y, self.levelZ)
                )


            testIntersect = {}
            for rmLine in self.BoundarysToCenter:
                if testLine.Intersect(rmLine, self.resultIntersect) == DB.SetComparisonResult.Overlap:

                    startXYZ = rmLine.GetEndPoint(0)
                    # округление до 7 знака
                    sumStartXYZ = str(round(startXYZ.X + startXYZ.Y + startXYZ.Z, 7))
                    # если есть пересечение, им может быть и прохождение через вершину
                    if testLine.Distance(startXYZ) == 0.0:
                        if sumStartXYZ not in testIntersect:
                            testIntersect[sumStartXYZ] = 1

                    endXYZ = rmLine.GetEndPoint(1)
                    sumEndXYZ = str(round(endXYZ.X + endXYZ.Y + endXYZ.Z, 7))
                    # если есть пересечение, им может быть и прохождение через вершину
                    if testLine.Distance(endXYZ) == 0.0:
                        if sumEndXYZ not in testIntersect:
                            testIntersect[sumEndXYZ] = 1

                    # если не проходит через вершину = ни через начало, ни через конец ганицы
                    if testLine.Distance(startXYZ) != 0.0 and testLine.Distance(endXYZ) != 0.0:
                        # XYZ центров линий, чтоб были отличающимися от вершин
                        centerLineXYZ = rmLine.Evaluate(0.5, True)
                        currentKey = str(round(centerLineXYZ.X + centerLineXYZ.Y + centerLineXYZ.Z, 7))
                        if currentKey not in testIntersect:
                            testIntersect[currentKey] = 1

            # ЕСЛИ КОЛИЧЕСТВО ПЕРЕСЕЧЕНИЙ/ПАР КЛЮЧ-ЗНАЧЕНИЕ В СЛОВАРЕ РАВНО НУЛЮ = ВНЕ ПОМЕЩЕНИЯ
            # остаток от деления нуля на 2 тоже ноль = четное
            if len(testIntersect) == 0:
                return False

            # ЕСЛИ КОЛИЧЕСТВО ПЕРЕСЕЧЕНИЙ/ПАР КЛЮЧ-ЗНАЧЕНИЕ В СЛОВАРЕ ЧЕТНОЕ = ВНЕ ПОМЕЩЕНИЯ
            if len(testIntersect) % 2 == 0:
                return False

            # ЕСЛИ КОЛИЧЕСТВО ПЕРЕСЕЧЕНИЙ/ПАР КЛЮЧ-ЗНАЧЕНИЕ В СЛОВАРЕ НЕЧЕТНОЕ = ВНУТРИ ПОМЕЩЕНИЯ
            if len(testIntersect) % 2 != 0:
                return True

# Equal - совпадение двух линий (частичное совпадение неодинаковых линий, но лежащих одна в другой или совпадение абсолютных копий двух линий)
# Overlap - пересечение (Перекрытие двух наборов/линий не является пустым и строгим подмножеством обоих наборов)
# Disjoint - непересекающиеся/несвязаны (Оба набора/линии не пусты и не перекрываются)
