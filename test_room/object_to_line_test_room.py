# module object_to_line_test_room.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


class ObjectToLine(object):

    def __init__(self, lineOrXYZ, room, lengthOutLine = 7):
        self.room = room
        self.lineOrXYZ = lineOrXYZ
        self.lengthOutLine = lengthOutLine
        self.levelZ = self.room.Level.Elevation
        self.createdLine = self.getCreatedLine()

    def getCreatedLine(self):
        """
        создает линию из Line, или из XYZ, нужной длины
        на уровне координаты Z уровня помещения
        по умолчанию создается минимальная линия 7мм
        """

        # создаем трансляцию смещения, по умолчанию на 7мм по оси Y
        transformDefault = DB.Transform.CreateTranslation(DB.XYZ(
            0,
            # минимальная длина для короба 3мм, а мы по умолчанию зададим 7мм
            DB.UnitUtils.ConvertToInternalUnits(self.lengthOutLine, DB.UnitTypeId.Millimeters),
            0))
    
        if isinstance(self.lineOrXYZ, DB.Line):

            minimumStartPoint = DB.XYZ(
                    self.lineOrXYZ.GetEndPoint(0).X,
                    self.lineOrXYZ.GetEndPoint(0).Y,
                    self.levelZ)
            # если линия расположена вертикально, её проекция будет точкой
            if self.lineOrXYZ.Direction.Normalize().Z == 1:

                return DB.Line.CreateBound(
                        minimumStartPoint,
                        DB.Point.Create(transformDefault.OfPoint(minimumStartPoint)).Coord
                        )

            else:
                # если линия горизонтальная или не строго вертикальная
                startXYZ = self.lineOrXYZ.GetEndPoint(0)
                endXYZ = self.lineOrXYZ.GetEndPoint(1)
                projectStartXYZ = DB.XYZ(startXYZ.X, startXYZ.Y, self.levelZ)
                projectEndXYZ = DB.XYZ(endXYZ.X, endXYZ.Y, self.levelZ)
                vectorOnPlaneProect = (projectEndXYZ - projectStartXYZ)

                # создаем трансляцию смещения по вектору направления линии
                transformAtAnAngle = DB.Transform.CreateTranslation(
                    vectorOnPlaneProect.Normalize() * DB.UnitUtils.ConvertToInternalUnits(self.lengthOutLine, DB.UnitTypeId.Millimeters)
                    )

                # вектор проекции линии, а не самой линии

                # если между проекциями точек начала и конца линии расстояние меньше 7мм
                if projectStartXYZ.DistanceTo(projectEndXYZ) < DB.UnitUtils.ConvertToInternalUnits(7, DB.UnitTypeId.Millimeters):

                    return DB.Line.CreateBound(
                            minimumStartPoint,
                            # DB.Point.Create(transformAtAnAngle.OfPoint(minimumStartPoint)).Coord
                            DB.Point.Create(transformDefault.OfPoint(minimumStartPoint)).Coord
                            )

                else:
                    # если между проекциями точек расстояние больше либо равно 7мм


                    # если длина линии по умолчанию
                    if self.lengthOutLine == 7:
                        return DB.Line.CreateBound(
                                projectStartXYZ,
                                projectEndXYZ
                                )

                    # если длина линии по умолчанию
                    else:
                        return DB.Line.CreateBound(
                                minimumStartPoint,
                                DB.Point.Create(transformAtAnAngle.OfPoint(minimumStartPoint)).Coord
                                )

        if isinstance(self.lineOrXYZ, DB.XYZ):
            miniStartPoint = DB.XYZ(
                    self.lineOrXYZ.X,
                    self.lineOrXYZ.Y,
                    self.levelZ)

            return DB.Line.CreateBound(
                    miniStartPoint,
                    DB.Point.Create(transformDefault.OfPoint(miniStartPoint)).Coord
                    )
