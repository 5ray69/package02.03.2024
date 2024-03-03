# module room_placed_test_room.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


class RoomPlaced(object):

    def __init__(self, room):
        self.room = room
        # self.checkPlaced = self.checkPlaced()

    def checkPlaced(self):
        """
        возвращает 1 помещение размещено Placed
        возвращает 2 помещение не размещено NotPlaced
        возвращает 3 помещение не окружено NotEnclosed
        возвращает 4 помещение избыточное Redundant
        """

        # если помещение размещено
        if self.room.Area > 0 :
            return 1

        # если помещение не размещено
        elif not self.room.Location:
            return 2

        else:
            opt = DB.SpatialElementBoundaryOptions()

            # если помещение не окружено
            if not self.room.GetBoundarySegments(opt):
                return 3

            # если помещение избыточное, то его условие следующее:
            # if self.room.GetBoundarySegments(opt).Count == 0
            # но оно подходит и под предыдущий if, потому используем else
            else:
                return 4
