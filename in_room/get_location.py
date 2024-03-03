# -*- coding: utf-8 -*-
# module get_location.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


class PointLocationInRoom(object):
    def __init__(self, elem):
        self._elem = elem

    def getXYZ(self):
        """ВОЗВРАЩАЕТ XYZ"""
        # только для FamilyInstance и для LocationPoint, не для LocationCurve
        # если есть точка принадлежности помещению
        if self._elem.HasSpatialElementCalculationPoint :
            return self._elem.GetSpatialElementCalculationPoint()

        # если не возвращено обычное местоположение
        elif self._elem.Location.GetType().ToString().Contains("LocationPoint") :
            return self._elem.Location.Point

        else:
            return None

    def getPoint(self):
        """ВОЗВРАЩАЕТ Point"""
        # только для FamilyInstance и для LocationPoint, не для LocationCurve
        # если есть точка принадлежности помещению
        if self._elem.HasSpatialElementCalculationPoint:
            return DB.Point.Create(self._elem.GetSpatialElementCalculationPoint())

        # если не возвращено обычное местоположение
        elif self._elem.Location.GetType().ToString().Contains("LocationPoint"):
            return DB.Point.Create(self._elem.Location.Point)

        else:
            return None
