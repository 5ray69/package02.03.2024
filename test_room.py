# -*- coding: utf-8 -*
# module in_room.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List
# import json

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo

from test_room.user_warning_test_room import ErrorThereAreNoLevels, ErrorUserNoSelect,\
                                        ErrorEmptyParameter
from test_room.get_location_test_room import PointSpatialElementOrPointLocation
from test_room.boundary_intersect_test_room import BordersRoom
from test_room.object_to_line_test_room import ObjectToLine
from test_room.level_any_object_test_room import LevelAnyObject
from test_room.room_placed_test_room import RoomPlaced
from test_room.user_form_test_room import UserFormSelectLinkInstance


# если RevitLinkInstance есть, но GetLinkDocument() равна нулю (LinkInstan.GetLinkDocument() is None),
# то связь нужно через правую кнопку мыши Обновить
listLinkInstanceName = [LinkInstan.GetLinkDocument().Title for LinkInstan in FEC(doc).OfClass(DB.RevitLinkInstance) if LinkInstan.GetLinkDocument()]
userForm = UserFormSelectLinkInstance(listLinkInstanceName)
userForm.ShowDialog()

# ЕСЛИ ПОЛЬЗОВАТЕЛЬ НИЧЕГО НЕ ВЫБРАЛ
if not userForm.listUserSelect:
    raise ErrorUserNoSelect()

# экземпляр связи
LinkInstance = [LinkInstan for LinkInstan in FEC(doc).OfClass(DB.RevitLinkInstance) if userForm.listUserSelect[0] in LinkInstan.Name][0]
# документ связи
LinkDoc = LinkInstance.GetLinkDocument()
# # типоразмер связи
# LinkType = doc.GetElement(LinkInstance.GetTypeId())
# трансформация из связи
LinkTransform = LinkInstance.GetTotalTransform()
# OUT = LinkDoc.Title

displayUnits = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()

categories = [
    DB.BuiltInCategory.OST_ElectricalFixtures,  # здесь вложенные семейства (другой подход) электрические приборы
    DB.BuiltInCategory.OST_ElectricalEquipment,  # здесь вложенные семейства (другой подход) электрооборудование
    DB.BuiltInCategory.OST_LightingDevices,  # здесь без вложенных семейств (один подход) выключатели
    DB.BuiltInCategory.OST_LightingFixtures,  # здесь без вложенных семейств (один подход) осветительные приборы
    DB.BuiltInCategory.OST_Conduit,  # здесь без вложенных семейств (один подход) короба
    DB.BuiltInCategory.OST_ConduitFitting,  # без вложенных семейств (один подход) соденительные детали коробов
    DB.BuiltInCategory.OST_CableTray,  # без вложенных семейств (один подход) кабельные лотки
    DB.BuiltInCategory.OST_CableTrayFitting,  # здесь вложенные семейства  (другой подход)соденительные детали кабельных лотков
    DB.BuiltInCategory.OST_ElectricalCircuit,  # электрические цепи
    DB.BuiltInCategory.OST_FireAlarmDevices,  # без вложенных семейств (один подход) пожарная сигнализация
    DB.BuiltInCategory.OST_MechanicalEquipment  # категория оборудование, есть вложенные семейства, не общие
]

multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))
OUT = []
with DB.Transaction(doc, 'test_room') as t:
    t.Start()
    for room in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_Rooms):
        # если помещение размещено, исключаем неразмещенные, неокруженные и избыточные
        if RoomPlaced(room).checkPlaced() == 1:
            paramRoomName = room.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()
            paramRoomNumber = room.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString()
            paramRoomFlat = room.LookupParameter('БУДОВА_Номер квартиры').AsString()

            for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():

                # ПОЛЬЗОВАТЕЛЬСКИЕ СЕМЕЙСТВА, СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ КОРОБОВ И КАБЕЛЬНЫХ ЛОТКОВ
                if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Номер квартиры'):
                    # если это не полоса заземления, категория пожарная сигнализация
                    if el.Category.Id != DB.ElementId(DB.BuiltInCategory.OST_FireAlarmDevices):
                        # соединительные детали кабельных лотков и соединительные детали коробов тоже здесь
                        # если семейство не вложенное
                        if el.SuperComponent is None:

                            # # если БУДОВА_Этаж не заполнен
                            # paramLevel = el.LookupParameter('БУДОВА_Этаж')
                            # if paramLevel.AsString() is None or paramLevel.AsString() == "":
                            #     paramLevel.Set(LevelAnyObject(doc, el).getLevelName())

                            # если имя уровня элемента равно имени уровня помещения
                            if LevelAnyObject(doc, el).getLevelName() == room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString():

                                paramElemFlat = el.LookupParameter('БУДОВА_Номер квартиры')
                                # если БУДОВА_Номер квартиры не заполнен
                                if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "":

                                    # XYZ РАСПОЛОЖЕНИЯ ЭЛЕМЕНТА
                                    # если нет точки размещения в помещении, то будет извлечена точка размещения семейства
                                    xyzLocation = PointSpatialElementOrPointLocation(el).getXYZSpatialElementOrPointLocation()

                                    # НАХОДИТСЯ ЛИ ЭЛЕМЕНТ В ПОМЕЩЕНИИ
                                    bordersRoom1 = BordersRoom(
                                                        room,
                                                        ObjectToLine(xyzLocation, room).getCreatedLine(),
                                                        LinkTransform
                                                        )
                                    # ЕСЛИ ОБЪЕКТ В ПОМЕЩЕНИИ
                                    if bordersRoom1.insideTheBorders():

                                        paramElemName = el.LookupParameter('BDV_E000_Имя помещения')
                                        paramElemNumber = el.LookupParameter('BDV_E000_Номер помещения')

                                        if paramElemName.AsString() is None or paramElemName.AsString() == "": paramElemName.Set(paramRoomName)
                                        if paramElemNumber.AsString() is None or paramElemNumber.AsString() == "": paramElemNumber.Set(paramRoomNumber)
                                        if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "": paramElemFlat.Set(paramRoomFlat)

                # ЭЛЕКТРИЧЕСКИЕ ЦЕПИ
                if isinstance(el, DB.Electrical.ElectricalSystem):
                    baseEquip = el.BaseEquipment
                    # если цепь подключена
                    if baseEquip:
                        # если имя уровня baseEquip равно имени уровня помещения
                        if LevelAnyObject(doc, baseEquip).getLevelName() == room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString():

                            paramElemFlat = el.LookupParameter('БУДОВА_Номер квартиры')
                            # # если БУДОВА_Номер квартиры не заполнен
                            if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "":

                                # XYZ РАСПОЛОЖЕНИЯ baseEquip
                                # если нет точки размещения в помещении, то будет извлечена точка размещения семейства
                                xyzLocation = PointSpatialElementOrPointLocation(baseEquip).getXYZSpatialElementOrPointLocation()

                                # НАХОДИТСЯ ЛИ baseEquip В ПОМЕЩЕНИИ
                                bordersRoom2 = BordersRoom(
                                                    room,
                                                    ObjectToLine(xyzLocation, room).getCreatedLine(),
                                                    LinkTransform
                                                    )
                                # ЕСЛИ baseEquip В ПОМЕЩЕНИИ
                                if bordersRoom2.insideTheBorders():

                                    paramElemName = el.LookupParameter('BDV_E000_Имя помещения')
                                    paramElemNumber = el.LookupParameter('BDV_E000_Номер помещения')

                                    if paramElemName.AsString() is None or paramElemName.AsString() == "": paramElemName.Set(paramRoomName)
                                    if paramElemNumber.AsString() is None or paramElemNumber.AsString() == "": paramElemNumber.Set(paramRoomNumber)
                                    if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "": paramElemFlat.Set(paramRoomFlat)


                # КОРОБА И КАБЕЛЬНЫЕ ЛОТКИ
                # И ПОЛОСА ЗАЗЕМЛЕНИЯ (КАТЕГОРИЯ ПОЖАРНАЯ СИГНАЛИЗАЦИЯ el.Category.Id.IntegerValue == -2008085)
                # у соед.деталей коробов и кабельных лотков нет параметра Уровень спецификации, а есть параметр Базовый уровень
                # потому нужна отдельная обработка
                # если выполняется любое из условий (аналогично функция all - выполняются все условия)
                if any([
                    isinstance(el, DB.Electrical.Conduit),
                    isinstance(el, DB.Electrical.CableTray),
                    el.Category.Id == DB.ElementId(DB.BuiltInCategory.OST_FireAlarmDevices)
                    ]):

                    # если имя уровня объекта равно имени уровня помещения
                    # у полосы заземления, когда она по грани, нет привязки к уровню и не может быть, потому
                    # нужно сделать отдельную обратоку, когда рабочая плоскость <не привязано>, то пропускать извлечение уровня
                    # скрипт по захватке заполняет БУДОВА_Этаж и из него можно считывать, но лучше пропускать вообще это размещение,
                    # так как оно должно быть в in_room, она точно находится в помещении, не внутри стены, а на ее грани
                    if LevelAnyObject(doc, el).getLevelName() == room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString():

                        paramElemFlat = el.LookupParameter('БУДОВА_Номер квартиры')
                        # если БУДОВА_Номер квартиры не заполнен
                        if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "":

                            # НАХОДИТСЯ ЛИ baseEquip В ПОМЕЩЕНИИ
                            bordersRoom3 = BordersRoom(
                                                room,
                                                ObjectToLine(el.Location.Curve, room).getCreatedLine(),
                                                LinkTransform
                                                )
                            # ЕСЛИ ОБЪЕКТ В ПОМЕЩЕНИИ
                            if bordersRoom3.insideTheBorders():

                                paramElemName = el.LookupParameter('BDV_E000_Имя помещения')
                                paramElemNumber = el.LookupParameter('BDV_E000_Номер помещения')
                                paramElemFlat = el.LookupParameter('БУДОВА_Номер квартиры')

                                if paramElemName.AsString() is None or paramElemName.AsString() == "": paramElemName.Set(paramRoomName)
                                if paramElemNumber.AsString() is None or paramElemNumber.AsString() == "": paramElemNumber.Set(paramRoomNumber)
                                if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "": paramElemFlat.Set(paramRoomFlat)
        else:
            if RoomPlaced(room).checkPlaced() == 2:
                OUT.append(["помещение не размещено Id = " + str(room.Id.IntegerValue)])
            if RoomPlaced(room).checkPlaced() == 3:
                OUT.append(["помещение не окружено Id = " + str(room.Id.IntegerValue)])
            if RoomPlaced(room).checkPlaced() == 4:
                OUT.append(["помещение избыточное Id = " + str(room.Id.IntegerValue)])
    t.Commit()
































































































# №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
# bool result = false;
# int j = size - 1;
# for (int i = 0; i < size; i++)
# {
#     if ( (p[i].Y < point.Y && p[j].Y >= point.Y || p[j].Y < point.Y && p[i].Y >= point.Y) && (p[i].X + (point.Y - p[i].Y) / (p[j].Y - p[i].Y) * (p[j].X - p[i].X) < point.X) )
#         result = !result;
#     j = i;
# }
# # p - список точек/вершин многоугольника
# # size - количество точек/вершин многоугольника
# # result - входит ли точка в многоугольник
# # point - точка, которая проверяется, лежит ли она в многоугольнике

# # Первая строка условия проверяет попадание point.Y между значениями p[i].Y и p[j].Y, 
# # контролирует направление прохода вершины и обеспечивает ненулевой знаменатель основной формулы.

# # Вторая строка проверяет нахождение стороны p[i]p[j] слева от точки point.

# # Третья строка формирует отрицательный ответ при чётном количестве сторон слева и положительный — при нечётном.

# В основе алгоритма лежит идея подсчёта количества пересечений луча, исходящего из данной точки в направлении горизонтальной оси, 
# со сторонами многоугольника. Если оно чётное, точка не принадлежит многоугольнику. В данном алгоритме луч направлен влево.

# №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
# В основе алгоритма лежит идея подсчёта количества пересечений луча, исходящего из данной точки в направлении горизонтальной оси,
#  со сторонами многоугольника. Если оно чётное, точка не принадлежит многоугольнику. В данном алгоритме луч направлен влево.
# npol - количество вершин многоугольника

#   bool pnpoly(int npol, float * xp, float * yp, float x, float y)
#   {
#     bool c = false;
#     for (int i = 0, j = npol - 1; i < npol; j = i++) 
#     {
#       if ((((yp[i] <= y) && (y < yp[j])) || ((yp[j] <= y) && (y < yp[i]))) && (((yp[j] - yp[i]) != 0) && (x > ((xp[j] - xp[i]) * (y - yp[i]) / (yp[j] - yp[i]) + xp[i]))))
#           c = !c;
#     }
#     return c;
#   }
# Замечание: Так как умножение быстрее деления, условие можно записать так:

#   int pnpoly(int npol, float * xp, float * yp, float x, float y)
#   {
#     int c = 0;
#     for (int i = 0, j = npol - 1; i < npol; j = i++) 
#     {
#       if ((
#         (yp[i] < yp[j]) && (yp[i] <= y) && (y <= yp[j]) && ((yp[j] - yp[i]) * (x - xp[i]) > (xp[j] - xp[i]) * (y - yp[i]))
#       ) || (
#         (yp[i] > yp[j]) && (yp[j] <= y) && (y <= yp[i]) && ((yp[j] - yp[i]) * (x - xp[i]) < (xp[j] - xp[i]) * (y - yp[i]))
#       ))
#         c = !c;
#     }
#     return c;
#   }
# Однако, стоит заметить, что данный алгоритм не эквивалентен предыдущему, поэтому его использование может привести к неправильным результатам.
# №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
# На Python программа несколько отличается от других языков в сторону компактности из-за особенностей адресации элементов массива. Не нужны дополнительные переменные. Не работает с многоугольниками вогнутого типа.

#  def inPolygon(x, y, xp, yp):
#     c=0
#     for i in range(len(xp)):
#         if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])): 
#              c = 1 - c 
#     return c
 
#  print( inPolygon(100, 0, (-100, 100, 100, -100), (100, 100, -100, -100)))
# Быстрый алгоритм для случая, когда луч пересекает одну или несколько вершин
# Функция Cross определяет, пересекает ли луч j-ое ребро многоугольника:

#   bool Cross(int j)
#   {
#     int first = j;
#     int second = j == n - 1 ? 0 : j + 1;
#     double y = (xh - points[first].x) * (points[second].y - points[first].y) / (points[second].x - points[first].x) + points[first].y;
#     double minimal = min(points[first].x, points[second].x);
#     double maximal = max(points[first].x, points[second].x);
#     return (points[first].x != points[second].x) && (yh >= y) && (xh > minimal) && (xh <= maximal);
#   }
# Фрагмент основной программы:

#   ...
#   int count = 0;
#   for (int i = 0; i < n; i++)
#   {
#     count += Cross(i);
#   }
#   ...
# Если переменная count примет нечетное значение, то точка лежит внутри многоугольника. В противном случает точка лежит вне заданого многоугольника.

# Замечание: В данной реализации алгоритма луч направлен вниз.
# №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№


















# Пусть луч направлен горизонтально вправо.

# Для каждой пары смежных точек:

# 1.Сначала проверяете, лежит ли пара точек (краев отрезка) по одну сторону луча. Если по одну сторону - то луч не пересекает сторону.
# 2.Если по разные стороны - нужно найти точку пересечения луча и прямой, проходящей через две данные точки. Это аналитическая геометрия, по сути, решение приводить не буду. Если точка пересечения правее точки, откуда исходит луч - значит пересечение есть.

# Нужно учитывать специальный случай, когда луч проходит через вершину многоугольника:

# 1.Если вторые точки обоих отрезков, которым принадлежит данная вершина находятся по одну сторону от луча, то считать это двумя пересечениями (или отсутствием пресечения - четность будет та же)
# 2.Если вторые точки по разные стороны луча - считать одним пересечением.
# №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№

























# # module s4.3.6.py
# # -*- coding: utf-8 -*-
# import clr
# clr.AddReference('RevitAPI')
# from Autodesk.Revit import DB
# from Autodesk.Revit.DB import Architecture as AR
# from Autodesk.Revit.DB import FilteredElementCollector as FEC
# from System.Collections.Generic import List


# import sys
# sys.path += [
#     r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
# ]

# uiapp = __revit__  #noqa
# app = __revit__.Application  #noqa
# uidoc = uiapp.ActiveUIDocument  #noqa
# doc = __revit__.ActiveUIDocument.Document  # noqa

# # Выбрали вид, на котором нужно создать цветовую область
# # view = [v for v in FEC(doc).OfClass(DB.ViewPlan).ToElements() if v.Name == '01 - Entry Level']


# # Имя типа цветовой области - Wood 1.
# fill_Id = [fill.Id for fill in FEC(doc).OfClass(DB.FilledRegionType).ToElements() if fill.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == 'Wood 1']

# # Instruction - по поверхности сердцевины;
# # Cafeteria - по осевой линии сердцевины;
# # Electrical - по чистовой поверхности.

# # Finish	Spatial element finish face. финшная/чистовая поверхность
# # Center	Spatial element centerline. центральная/осевая линия
# # CoreBoundary	Spatial element core boundary. граница ядра/сердцевины
# # CoreCenter	Spatial element core center. центр ядра/сердцевины


# # назначаем переменную на свойство
# roomoptions = DB.SpatialElementBoundaryOptions()

# with DB.Transaction(doc, 'Create FilledRegion') as t:
#     t.Start()
#     curveloops = []
#     # curveloops = List[DB.CurveLoop]()
#     # получаем помещения на активном виде
#     for room in FEC(doc, doc.ActiveView.Id).WherePasses(AR.RoomFilter()):
#         if room.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString() == 'Instruction':
#             # установили свойство границы помещения по поверхности сердцевины
#             roomoptions.SpatialElementBoundaryLocation = DB.SpatialElementBoundaryLocation.CoreBoundary
#             for bound_segments in room.GetBoundarySegments(roomoptions):
#                 # создали типизированный список кривых
#                 curves_list = List[DB.Curve]()
#                 for bound_segment in bound_segments:
#                     curves_list.Add(bound_segment.GetCurve())
#                 curveloops.append(DB.CurveLoop().Create(curves_list))

#         if room.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString() == 'Cafeteria':
#             # установили свойство границы помещения по осевой линии сердцевины
#             roomoptions.SpatialElementBoundaryLocation = DB.SpatialElementBoundaryLocation.CoreCenter
#             for bound_segments in room.GetBoundarySegments(roomoptions):
#                 # создали типизированный список кривых
#                 curves_list = List[DB.Curve]()
#                 for bound_segment in bound_segments:
#                     curves_list.Add(bound_segment.GetCurve())
#                 curveloops.append(DB.CurveLoop().Create(curves_list))

#         if room.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString() == 'Electrical':
#             # установили свойство границы помещения по чистовой поверхности
#             roomoptions.SpatialElementBoundaryLocation = DB.SpatialElementBoundaryLocation.Finish
#             for bound_segments in room.GetBoundarySegments(roomoptions):
#                 # создали типизированный список кривых
#                 curves_list = List[DB.Curve]()
#                 for bound_segment in bound_segments:
#                     curves_list.Add(bound_segment.GetCurve())
#                 curveloops.append(DB.CurveLoop().Create(curves_list))
#                 # curveloops.Add(DB.CurveLoop().Create(curves_list))

#     DB.FilledRegion.Create(
#         doc,
#         fill_Id[0],
#         doc.ActiveView.Id,
#         curveloops
#     )
#     t.Commit()







# uiapp = __revit__                          # noqa
# app = __revit__.Application                # noqa
# uidoc = __revit__.ActiveUIDocument         # noqa
# doc = __revit__.ActiveUIDocument.Document  # noqa


# #  свойство .IncludeNonVisibleObjects для получения скрытой геометрии
# g_options = DB.Options()
# g_options.IncludeNonVisibleObjects = True  # чтоб изменить свойство нужно использовать оператор присваивания (знак равно) присвоили свойству значение труе

# # отбираем поверхности расположенные по середине стен
# center_planar_face = {}
# for wall in FEC(doc).OfClass(DB.Wall):
#     # Перебираем солиды скрытых элементов
#     for solid in wall.Geometry[g_options]:
#         # получили FaceArray из солида
#         for planar_face in solid.Faces:
#             # Проверяем на пересечение поверхности и линии размещения стены на значение
#             # подмножество (Subset). Линия размещения всегда по центру при любых настройках
#             if planar_face.Intersect(wall.Location.Curve) == DB.SetComparisonResult.Subset:
#                 # Отбираем только вертикальные поверхности
#                 if not (planar_face.XVector.Z == 0 and planar_face.YVector.Z == 0):
#                     # сколько бы ни было поверхностей в словаре окажется только одна из них
#                     center_planar_face[wall] = planar_face

# # получили трансформацию из экземпляра связи
# mep_link_data = get_link_data(doc, 'IronPython_4408_Q_Intersection')
# # к линии размещения воздуховодов применили трансформацию из экземпляра связи
# # чтобы получить размещение линий в координатах основного файла
# duct_curves = [
#     duct.Location.Curve
#     .CreateTransformed(mep_link_data['instances'][0].GetTotalTransform())
#     for duct in FEC(mep_link_data['doc']).OfClass(DB.Mechanical.Duct)
# ]

# # типизированная переменная
# resultIntersect = clr.Reference[DB.IntersectionResultArray]()

# list_1 = []
# list_2 = []
# for key, value in center_planar_face.items():
#     str_type = key.WallType.Parameter[
#         DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()
#     for duct_curve in duct_curves:
#         # проеверяем на пересечение поверхности и линии (Overlap - пересекается)
#         if value.Intersect(duct_curve, resultIntersect) == DB.SetComparisonResult.Overlap:
#             if str_type == 'Типовой - 200мм':
#                 value.Intersect(duct_curve, resultIntersect)
#                 list_1.append(resultIntersect.Item[0].XYZPoint.X)
#                 list_1.append(resultIntersect.Item[0].XYZPoint.Y)
#                 list_1.append(resultIntersect.Item[0].XYZPoint.Z)
#             else:
#                 value.Intersect(duct_curve, resultIntersect)
#                 list_2.append(resultIntersect.Item[0].XYZPoint.X)
#                 list_2.append(resultIntersect.Item[0].XYZPoint.Y)
#                 list_2.append(resultIntersect.Item[0].XYZPoint.Z)
# # из первого списка вычли второй, перевели в мм и округлили до целого
# print(int(round(Unit(doc, sum(list_1) - sum(list_2), False).display)))


# start_xyz = wall.Location.Curve.GetEndPoint(0)
# end_xyz = wall.Location.Curve.GetEndPoint(1)
# # создаем вектор вычтя объекты XYZ один из другого
# v = end_xyz - start_xyz

# # создаем трансформацию смещения на 500мм по оси Z
# transform = DB.Transform.CreateTranslation(DB.XYZ(0, 0, Unit(doc, 500).internal))
# # создали точку, взяв центр Location.Curve стены, переместив объект xyz на 500мм по оси Z
# point = DB.Point.Create(transform.OfPoint(wall.Location.Curve.Evaluate(0.5, True)))

# Проецирует указанную точку на эту кривую
# Curve.Project(XYZ)

# Возвращает расстояние от этой точки до указанной точки
# XYZ.DistanceTo(XYZ)

# Вычисляет пересечение этой кривой с указанной кривой.
# Line.Intersect(Curve)

# Проецируем точку на плоскость и определяем расстояние до плоскости
# если точка лежит на плоскости, то расстояние до не равно нулю
# face.Project(Point).Distance

# face.Intersect(wall.Location.Curve)
# Subset - подмножество (Оба набора не пусты, и левый набор является строгим подмножеством правого набора)
# Disjoint - несвязный (Оба набора не пусты и не перекрываются)
# Overlap - наложение (Перекрытие двух наборов не является пустым и строгим подмножеством обоих наборов)

# HostObjectUtils.GetSideFaces(wall, ShellLayerType.Exterior) получение наружной грани

# Чтобы в python заработал метод Face.Intersect(Curve, IntersectionResultArray)
# resultArray = clr.Reference[DB.IntersectionResultArray]()
# face.Intersect(wall.Location.Curve, resultArray)

# Кривая расположения стены и общая толщина стены:
# wall.Location (объект LocationCurve)
# wall.WallType.Width (объект double)

# Итак, вы хотите увидеть, находится ли определенная точка на поверхности или нет?
# В этом случае вы можете просто использовать метод Face.Project(). Если он
#  возвращает null, это означает, что точка точно не на грани. В противном
#  случае сравните результат проекции и исходную точку, если они совпадают,
#  это означает, что исходная точка находится на грани.


