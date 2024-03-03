# module boundary_intersect_test_room.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
# from Autodesk.Revit.DB import FilteredElementCollector as FEC
# from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

from count_intersections_with_polygon_test_room import CountIntersectionsWithPolygon
from object_to_line_test_room import ObjectToLine


class BordersRoom(object):
    resultIntersect = clr.Reference[DB.IntersectionResultArray]()

    def __init__(self, room, projectLine, linkTransform):
        self.room = room
        self.projectLine = projectLine  # линия спроецированная на плоскость уровня помещения
        self.linkTransform = linkTransform
        self.levelZ = self.room.Level.Elevation
        self.bordersToCenter = self.getBordersToCenter()

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

    def insideTheBorders(self):
        """ВОЗВРАЩАЕТ TRUE ЕСЛИ ПРОЕКЦИЯ ЛИНИИ ПЕРЕСЕКАЕТ ГРАНИЦУ ПОМЕЩЕНИЯ.
        Принимает Line или XYZ (полученые из Location объектов)
        Сколько бы пересечений с границей помещения ни было и где б они ни были,
        то объект в помещении.
        Даже если одна точка/край линии лежит на границе помещения, а вся остальная часть линии вне.
        Если линия совпадает с линией границы помещения, то объект в помещении."""

        for roomLine in self.bordersToCenter:

            # ЕСЛИ ЕСТЬ ЛЮБОЕ СОВПАДЕНИЕ/НАЛОЖЕНИЕ ПРОЕКЦИИ НА ГРАНИЦУ ПОМЕЩЕНИЯ, ТО ОБЪЕКТ В ПОМЕЩЕНИИ
            # любое совпадение/наложение - это или наложение/совпадение точных копий,
            # или наложение/совпадение линий не равной длины с смещениями относительно начала или конца
            if self.projectLine.Intersect(roomLine, self.resultIntersect) == DB.SetComparisonResult.Equal:
                return True

        # ЕСЛИ ПРОЕКЦИЯ ЛИНИИ ПЕРЕСЕКАЕТ ГРАНИЦУ ПОМЕЩЕНИЯ, ТО ОБЪЕКТ В ПОМЕЩЕНИИ
        # проекция линии без удлинения нужна прежде удлиненной линии потому, что
        # линия может заходить извне и обрываться в помещении, тогда ее удлинение,
        # даст два пересечения границы помещения, что соотвествует условию
        # нахождения тестовой удлиненной линии вне помещения
        # ЗДЕСЬ ПРОЕКЦИЯ ЛИНИИ БЕЗ УДЛИНЕНИЯ
        countIntersectionsWithPolygon1 = CountIntersectionsWithPolygon(self.bordersToCenter, self.projectLine)
        projectIntersect = countIntersectionsWithPolygon1.getDictionary()

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
            testLength = ObjectToLine(self.projectLine, self.room, 70000).getCreatedLine()
            countIntersectionsWithPolygon2 = CountIntersectionsWithPolygon(self.bordersToCenter, testLength)
            testIntersect = countIntersectionsWithPolygon2.getDictionary()

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

# if self.projectLine.Intersect(roomLine, self.resultIntersect) == DB.SetComparisonResult.Equal:
# Equal - совпадение двух линий (частичное совпадение неодинаковых линий, но лежащих одна в другой или совпадение абсолютных копий двух линий)
# Overlap - пересечение (Перекрытие двух наборов/линий не является пустым и строгим подмножеством обоих наборов)
# Disjoint - непересекающиеся/несвязаны (Оба набора/линии не пусты и не перекрываются)
