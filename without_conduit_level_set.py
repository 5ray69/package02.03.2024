# module create_conduit_for_tech_level.py
# -*- coding: utf-8 -*

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List

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

from conduit_level_set.user_warning_conduit_level_set import ErrorThereAreNoLevels, ErrorUserNoSelect,\
                                        ErrorEmptyParameter
from conduit_level_set.user_form_level_set import UserFormSelectLinkInstance


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


with DB.Transaction(doc, 'conduit_level_set') as t:
    t.Start()
    categories = [
        DB.BuiltInCategory.OST_Conduit,
        DB.BuiltInCategory.OST_ConduitFitting
    ]

    multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))

    for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():
        # СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ КОРОБА
        if el.Category.Id == DB.ElementId(DB.BuiltInCategory.OST_ConduitFitting):
            # записали из параметра Уровень
            el.LookupParameter('БУДОВА_Уровень оборудования').Set(
                doc.GetElement(el.LevelId).Name[1:3])
            # записали из параметра Уровень
            el.LookupParameter('БУДОВА_Этаж').Set(
                doc.GetElement(el.LevelId).Name)

        # КОРОБА
        if isinstance(el, DB.Electrical.Conduit):
            # записали из параметра Базовый уровень
            el.LookupParameter('БУДОВА_Уровень оборудования').Set(
                doc.GetElement(el.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name[1:3])
            # записали из параметра Базовый уровень
            el.LookupParameter('БУДОВА_Этаж').Set(
                doc.GetElement(el.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name)
            # если короб находится в стяжке, те ниже уровня пола (-1.31234 = -400мм)
            if el.LevelOffset < 0 and el.LevelOffset > -1.31234:
                point0 = el.Location.Curve.GetEndPoint(0)
                point1 = el.Location.Curve.GetEndPoint(1)
                # минус минус дает плюс, подымаем проверочную точку из стяжку в помещение
                checkPoint0 = DB.XYZ(point0.X, point0.Y, point0.Z - el.LevelOffset)
                checkPoint1 = DB.XYZ(point1.X, point1.Y, point1.Z - el.LevelOffset)
                for room in FEC(LinkDoc).OfCategory(DB.BuiltInCategory.OST_Rooms):
                    # если этаж короба равна этажу помещения
                    if doc.GetElement(el.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name == \
                        room.Parameter[DB.BuiltInParameter.LEVEL_NAME].AsString():
                        if room.IsPointInRoom(LinkTransform.OfPoint(checkPoint0)) or room.IsPointInRoom(LinkTransform.OfPoint(checkPoint1)):
                            RoomName = room.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()
                            FlatNumber = room.LookupParameter('БУДОВА_Номер квартиры').AsString()
                            RoomNumber = room.Parameter[DB.BuiltInParameter.ROOM_NUMBER].AsString()
                            if RoomName:
                                el.LookupParameter('BDV_E000_Имя помещения').Set(RoomName)
                            if FlatNumber:
                                el.LookupParameter('БУДОВА_Номер квартиры').Set(FlatNumber)
                            if RoomNumber:
                                el.LookupParameter('BDV_E000_Номер помещения').Set(RoomNumber)

                            # если параметр не пуст
                            if el.LookupParameter('Стиль коробов').AsElementId().IntegerValue != -1:
                                if "метпласт" in doc.GetElement(el.LookupParameter('Стиль коробов').AsElementId()).Name:
                                    # Получаем подключенную к коробу соед.деталь, она находится в стене, вне помещения
                                    conConduit = [con for con in el.ConnectorManager.Connectors if con.IsConnected][0]
                                    conFit = [nCon for nCon in conConduit.AllRefs 
                                        if conConduit.Owner.Id != nCon.Owner.Id][0]
                                    fit = conFit.Owner
                                    if RoomName:
                                        fit.LookupParameter('BDV_E000_Имя помещения').Set(RoomName)
                                    if FlatNumber:
                                        fit.LookupParameter('БУДОВА_Номер квартиры').Set(FlatNumber)
                                    if RoomNumber:
                                        fit.LookupParameter('BDV_E000_Номер помещения').Set(RoomNumber)

                                    # Получаем короб, подключенный к соед.детали, идущий вертикально вверх
                                    conFitting = [fCon for fCon in fit.MEPModel.ConnectorManager.Connectors
                                        if conFit.Id != fCon.Id][0]
                                    conduitV = [conn.Owner for conn in conFitting.AllRefs][0]
                                    if RoomName:
                                        conduitV.LookupParameter('BDV_E000_Имя помещения').Set(RoomName)
                                    if FlatNumber:
                                        conduitV.LookupParameter('БУДОВА_Номер квартиры').Set(FlatNumber)
                                    if RoomNumber:
                                        conduitV.LookupParameter('BDV_E000_Номер помещения').Set(RoomNumber)

    t.Commit()
