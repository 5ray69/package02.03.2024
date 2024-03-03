# -*- coding: utf-8 -*-
# module get_location.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

from user_warning_location_test_room import ErrorXYZSpatialElementOrPointLocation, ErrorXYZSpatialElement, ErrorPointLocationPoint


class PointSpatialElementOrPointLocation(object):
    def __init__(self, elem):
        self._elem = elem

    def getXYZSpatialElementOrPointLocation(self):
        """ВОЗВРАЩАЕТ XYZ ТОЧКИ РАЗМЕЩЕНИЯ В ПОМЕЩЕНИИ А ЕСЛИ ЕЕ НЕТ ТО ТОЧКИ РАЗМЕЩЕНИЯ СЕМЕЙСТВА"""
        # только для FamilyInstance и для LocationPoint, не для LocationCurve
        # если есть точка принадлежности помещению
        if self._elem.HasSpatialElementCalculationPoint :
            return self._elem.GetSpatialElementCalculationPoint()

        # если не возвращено обычное местоположение
        elif self._elem.Location.GetType().ToString().Contains("LocationPoint") :
            return self._elem.Location.Point

        else:
            raise ErrorXYZSpatialElementOrPointLocation(self._elem)


    def getPointSpatialElementOrPointLocation(self):
        """ВОЗВРАЩАЕТ Point ТОЧКИ РАЗМЕЩЕНИЯ В ПОМЕЩЕНИИ А ЕСЛИ ЕЕ НЕТ ТО ТОЧКИ РАЗМЕЩЕНИЯ СЕМЕЙСТВА"""
        # только для FamilyInstance и для LocationPoint, не для LocationCurve
        # если есть точка принадлежности помещению
        if self._elem.HasSpatialElementCalculationPoint:
            return DB.Point.Create(self._elem.GetSpatialElementCalculationPoint())

        # если есть точка размещения семества
        elif self._elem.Location.GetType().ToString().Contains("LocationPoint"):
            return DB.Point.Create(self._elem.Location.Point)

        else:
            raise ErrorXYZSpatialElementOrPointLocation(self._elem)


    def getXYZSpatialElement(self):
        """ВОЗВРАЩАЕТ XYZ ТОЧКИ РАЗМЕЩЕНИЯ В ПОМЕЩЕНИИ"""
        # только для FamilyInstance и для LocationPoint, не для LocationCurve
        # если есть точка принадлежности помещению
        if self._elem.HasSpatialElementCalculationPoint :
            return self._elem.GetSpatialElementCalculationPoint()

        else:
            raise ErrorXYZSpatialElement(self._elem)


    def getPointSpatialElement(self):
        """ВОЗВРАЩАЕТ Point ТОЧКИ РАЗМЕЩЕНИЯ В ПОМЕЩЕНИИ"""
        # только для FamilyInstance и для LocationPoint, не для LocationCurve
        # если есть точка принадлежности помещению
        if self._elem.HasSpatialElementCalculationPoint:
            return DB.Point.Create(self._elem.GetSpatialElementCalculationPoint())

        else:
            raise ErrorXYZSpatialElement(self._elem)


    def getXYZSLocationPoint(self):
        """ВОЗВРАЩАЕТ XYZ ТОЧКИ РАЗМЕЩЕНИЯ СЕМЕЙСТВА"""
        # если есть точка размещения семества
        if self._elem.Location.GetType().ToString().Contains("LocationPoint"):
            return self._elem.Location.Point

        else:
            raise ErrorPointLocationPoint(self._elem)

    def getPointLocationPoint(self):
        """ВОЗВРАЩАЕТ Point ТОЧКИ РАЗМЕЩЕНИЯ СЕМЕЙСТВА"""
        # только для FamilyInstance и для LocationPoint, не для LocationCurve
        # если есть точка размещения семества
        if self._elem.Location.GetType().ToString().Contains("LocationPoint"):
            return DB.Point.Create(self._elem.Location.Point)

        else:
            raise ErrorPointLocationPoint(self._elem)
