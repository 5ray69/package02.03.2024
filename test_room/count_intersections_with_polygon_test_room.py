# module count_intersections_with_polygon_test_room.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
# clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
# from Autodesk.Revit.DB import FilteredElementCollector as FEC
# from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа


class CountIntersectionsWithPolygon(object):
    resultIntersect = clr.Reference[DB.IntersectionResultArray]()

    def __init__(self, roomBorders, projectLine):
        self.roomBorders = roomBorders  # границы на плоскости уровня помещения
        self.projectLine = projectLine  # линия спроецированная на плоскость уровня помещения

    def getDictionary(self):
        """ВОЗВРАЩАЕТ СЛОВАРЬ ДЛЯ ПОДСЧЕТА КОЛИЧЕСТВА ПЕРЕСЕЧЕНИЙ С МНОГОУГОЛЬНИКОМ ГРАНИЦ ПОМЕЩЕНИЯ
        количество пар ключ-значение равно количеству прохождений проекции линии через границу помещения"""

        projectIntersect = {}

        for roomLine in self.roomBorders:

            # если проекция линии пересекает границу помещения
            if self.projectLine.Intersect(roomLine, self.resultIntersect) == DB.SetComparisonResult.Overlap:

                # Проходя через вершину, линия пересекает две линии границы помещения сразу и дает 2 пересечения.
                # Если такая вершина уже есть в словаре, то второе пересечение ее же, но в другой линии,
                # не будет добавлено в словарь и будет зачтено как одно пересечение

                startXYZ = roomLine.GetEndPoint(0)
                sumStartXYZ = str(round(startXYZ.X + startXYZ.Y + startXYZ.Z, 7))  # округление до 7 знаков

                # если projectLine проходит через вершину = начальную точку линии границы
                if self.projectLine.Distance(startXYZ) == 0.0:
                    if sumStartXYZ not in projectIntersect:
                        projectIntersect[sumStartXYZ] = 1

                endXYZ = roomLine.GetEndPoint(1)
                sumEndXYZ = str(round(endXYZ.X + endXYZ.Y + endXYZ.Z, 7))

                # если projectLine проходит через вершину = конечную точку линии границы
                if self.projectLine.Distance(endXYZ) == 0.0:
                    if sumEndXYZ not in projectIntersect:
                        projectIntersect[sumEndXYZ] = 1

                # если projectLine не проходит
                # ни через вершину начальной точки линии границы,
                # ни через вершину конечной точки линии границы (пересекает где-то в другом месте линию границы)
                if self.projectLine.Distance(startXYZ) != 0.0 and self.projectLine.Distance(endXYZ) != 0.0:
                    centerLineXYZ = roomLine.Evaluate(0.5, True)
                    currentKey = str(round(centerLineXYZ.X + centerLineXYZ.Y + centerLineXYZ.Z, 7))
                    if currentKey not in projectIntersect:
                        projectIntersect[currentKey] = 1

        return projectIntersect
