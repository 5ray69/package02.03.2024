# module level_any_object_test_room.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC

from user_warning_levelid_or_host_test_room import ErrorElementDoesNotHaveLevel


class LevelAnyObject(object):

    def __init__(self, doc, el):
        self.doc = doc
        self.el = el

    def getLevelName(self):
        """извлекает имя уровня в виде строки
        """

        if self.el.Category.Id == DB.ElementId(DB.BuiltInCategory.OST_FireAlarmDevices):
            # если полоса заземления на грани (расположена вертикально)
            if self.el.Host is None:
                # минимльное значение Z края элемента (прямой)
                zElement = round(min(self.el.Location.Curve.GetEndPoint(0).Z, self.el.Location.Curve.GetEndPoint(1).Z), 3)
                # отметка самого нижнего уровня
                zLevelElevMin = sorted([lev.Elevation for lev in FEC(self.doc).OfClass(DB.Level)])[0]
                # если край элемента ниже самого нижнего уровня
                if zElement < zLevelElevMin:
                    return [lev.Name for lev in FEC(self.doc).OfClass(DB.Level) \
                                if round(lev.Elevation, 3) == round(zLevelElevMin, 3)][0]
                else:
                    # уровни, которые ниже отметки элемента
                    levelsElevBelow = [lev for lev in FEC(self.doc).OfClass(DB.Level) if lev.Elevation <= zElement]
                    # минимальная разница между Z уровня и Z элемента
                    differenceMin = sorted([zElement - lev.Elevation for lev in levelsElevBelow])[0]
                    # имя уровня с короторым разница минимальная, над которым элемент
                    return [lev.Name for lev in FEC(self.doc).OfClass(DB.Level) \
                                if round(zElement - lev.Elevation, 3) == round(differenceMin, 3)][0]

            else:
                return self.el.Host.Name

        if self.el.LevelId.IntegerValue != -1:
            return self.doc.GetElement(self.el.LevelId).Name

        if hasattr(self.el, "Host"):
            return self.el.Host.Name

        if hasattr(self.el, "ReferenceLevel"):
            return self.el.ReferenceLevel.Name

        # any интересуется значениями True и
        # возвращает True, находя первое из них,
        # или False — если не нашла ни одного
        if any([
            hasattr(self.el, "Host"),
            self.el.LevelId.IntegerValue != -1,
            hasattr(self.el, "ReferenceLevel")
        ]):
            raise ErrorElementDoesNotHaveLevel(self.el)
