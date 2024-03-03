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

from in_room.user_warning_in_room import ErrorThereAreNoLevels, ErrorUserNoSelect,\
                                        ErrorEmptyParameter
from in_room.get_location import PointLocationInRoom
from in_room.user_form_in_room import UserFormSelectLinkInstance


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
    DB.BuiltInCategory.OST_FireAlarmDevices  # без вложенных семейств (один подход) пожарная сигнализация
    # DB.BuiltInCategory.OST_MechanicalEquipment  # категория оборудование не использовалась, есть вложенные семейства, не общие
]

multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))
OUT = []
with DB.Transaction(doc, 'in_room') as t:
    t.Start()

    for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():

        # ПОЛЬЗОВАТЕЛЬСКИЕ СЕМЕЙСТВА, СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ КОРОБОВ И КАБЕЛЬНЫХ ЛОТКОВ
        if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Номер квартиры'):
            # если не полоса заземления, категория пожарная сигнализация
            if el.Category.Id.IntegerValue != -2008085:
                # соединительные детали кабельных лотков и соединительные детали коробов тоже здесь
                # если семейство не вложенное
                if el.SuperComponent is None:
                    # помещение, в котором находится точка размещения объекта
                    roomFromPoint = LinkDoc.GetRoomAtPoint(LinkTransform.OfPoint(PointLocationInRoom(el).getXYZ()))

                    # ПАРАМЕТРЫ ДЛЯ ЗАПОЛНЕНИЯ
                    # если объект не вне помещения, не None
                    if roomFromPoint:
                        paramRoomName = roomFromPoint.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()
                        paramRoomNumber = roomFromPoint.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString()
                        paramRoomFlat = roomFromPoint.LookupParameter('БУДОВА_Номер квартиры').AsString()

                        paramElemName = el.LookupParameter('BDV_E000_Имя помещения')
                        paramElemNumber = el.LookupParameter('BDV_E000_Номер помещения')
                        paramElemFlat = el.LookupParameter('БУДОВА_Номер квартиры')

                        if paramElemName.AsString() is None or paramElemName.AsString() == "": paramElemName.Set(paramRoomName)
                        if paramElemNumber.AsString() is None or paramElemNumber.AsString() == "": paramElemNumber.Set(paramRoomNumber)
                        if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "": paramElemFlat.Set(paramRoomFlat)

        # ЭЛЕКТРИЧЕСКИЕ ЦЕПИ
        if isinstance(el, DB.Electrical.ElectricalSystem):
            baseEquip = el.BaseEquipment
            # если цепь подключена
            if baseEquip:

                # помещение, в котором находится точка размещения объекта
                roomFromPoint = LinkDoc.GetRoomAtPoint(LinkTransform.OfPoint(PointLocationInRoom(baseEquip).getXYZ()))

                # ПАРАМЕТРЫ ДЛЯ ЗАПОЛНЕНИЯ
                # если объект не вне помещения, не None
                if roomFromPoint:
                    paramRoomName = roomFromPoint.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()
                    paramRoomNumber = roomFromPoint.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString()
                    paramRoomFlat = roomFromPoint.LookupParameter('БУДОВА_Номер квартиры').AsString()

                    paramElemName = el.LookupParameter('BDV_E000_Имя помещения')
                    paramElemNumber = el.LookupParameter('BDV_E000_Номер помещения')
                    paramElemFlat = el.LookupParameter('БУДОВА_Номер квартиры')

                    if paramElemName.AsString() is None or paramElemName.AsString() == "": paramElemName.Set(paramRoomName)
                    if paramElemNumber.AsString() is None or paramElemNumber.AsString() == "": paramElemNumber.Set(paramRoomNumber)
                    if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "": paramElemFlat.Set(paramRoomFlat)


        # КОРОБА И КАБЕЛЬНЫЕ ЛОТКИ, И ПОЛОСА ЗАЗЕМЛЕНИЯ (КАТЕГОРИЯ ПОЖАРНАЯ СИГНАЛИЗАЦИЯ el.Category.Id.IntegerValue == -2008085)
        # у соед.деталей коробов и кабельных лотков нет параметра Уровень спецификации, а есть параметр Базовый уровень
        # потому нужна отдельная обработка
        # если выполняется любое из условий (аналогично функция all - выполняются все условия)
        if any([
            isinstance(el, DB.Electrical.Conduit),
            isinstance(el, DB.Electrical.CableTray),
            el.Category.Id.IntegerValue == -2008085
            ]):

            # помещение, в котором находится первая точка короба/кабельного лотка
            # конечную el.Location.Curve.GetEndPoint(1) не учитываем
            # ЗДЕСЬ ВОЗМОЖНО МОЖНО ПЕРЕДЕЛАТЬ НА СРЕДНЮЮ ТОЧКУ ИЛИ СРАЗУ НА НЕСКОЛЬКО ТОЧЕК!!!!!!!!!!!!!!!!!!!!!!!!
            roomFromPoint = LinkDoc.GetRoomAtPoint(LinkTransform.OfPoint(el.Location.Curve.GetEndPoint(0)))

            # ПАРАМЕТРЫ ДЛЯ ЗАПОЛНЕНИЯ
            # если объект не вне помещения, не None
            if roomFromPoint:
                paramRoomName = roomFromPoint.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()
                paramRoomNumber = roomFromPoint.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString()
                paramRoomFlat = roomFromPoint.LookupParameter('БУДОВА_Номер квартиры').AsString()

                paramElemName = el.LookupParameter('BDV_E000_Имя помещения')
                paramElemNumber = el.LookupParameter('BDV_E000_Номер помещения')
                paramElemFlat = el.LookupParameter('БУДОВА_Номер квартиры')

                if paramElemName.AsString() is None or paramElemName.AsString() == "": paramElemName.Set(paramRoomName)
                if paramElemNumber.AsString() is None or paramElemNumber.AsString() == "": paramElemNumber.Set(paramRoomNumber)
                if paramElemFlat.AsString() is None or paramElemFlat.AsString() == "": paramElemFlat.Set(paramRoomFlat)

    t.Commit()


















# OUT = []
# for el in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
#     # ПОЛЬЗОВАТЕЛЬСКИЕ СЕМЕЙСТВА, СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ КОРОБОВ И КАБЕЛЬНЫХ ЛОТКОВ
#     if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Номер квартиры'):
#         # если не полоса заземления, категория пожарная сигнализация
#         if el.Category.Id.IntegerValue != -2008085:
#             # соединительные детали кабельных лотков и соединительные детали коробов тоже здесь
#             # если семейство не вложенное
#             if el.SuperComponent is None:
#                 roomFromPoint = LinkDoc.GetRoomAtPoint(LinkTransform.OfPoint(GetLocation(el)))
#                 OUT.append(roomFromPoint)


# OUT = []
# fam = [equip for equip in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment) 
#     if equip.Parameter[DB.BuiltInParameter.ALL_MODEL_MARK] and equip.Parameter[DB.BuiltInParameter.ALL_MODEL_MARK].AsString() == "96834"][0]
# for room in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_Rooms):
#     if room.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString() == "466":
#         if room.IsPointInRoom(LinkTransform.OfPoint(GetLocation(fam))):
#             OUT.append(True)
#         else:
#             OUT.append(False)







































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
