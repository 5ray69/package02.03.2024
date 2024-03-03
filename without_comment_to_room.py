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

categories = [
    DB.BuiltInCategory.OST_Conduit,  # здесь без вложенных семейств (один подход) короба
    DB.BuiltInCategory.OST_ConduitFitting,  # без вложенных семейств (один подход) соденительные детали коробов
    DB.BuiltInCategory.OST_ElectricalFixtures,  # здесь вложенные семейства (другой подход) электрические приборы
    DB.BuiltInCategory.OST_ElectricalCircuit,  # электрические цепи
    DB.BuiltInCategory.OST_ElectricalEquipment,  # здесь вложенные семейства (другой подход) электрооборудование
]

# ИЗ КОММЕНТАРИИ В НОМЕР КВАРТИРЫ
multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))
with DB.Transaction(doc, 'comment_to_room') as t:
    t.Start()
    for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():

        # КОРОБА И КАБЕЛЬНЫЕ ЛОТКИ
        # у соед.деталей коробов и кабельных лотков нет параметра Уровень спецификации, а есть параметр Базовый уровень
        # потому нужна отдельная обработка
        # если выполняется любое из условий (аналогично функция all - выполняются все условия)
        if any([
            isinstance(el, DB.Electrical.Conduit),
            isinstance(el, DB.Electrical.CableTray)
            ]):
            if el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString():
                if el.LookupParameter('БУДОВА_Номер квартиры').AsString() is None or el.LookupParameter('БУДОВА_Номер квартиры').AsString() == "":
                    el.LookupParameter('БУДОВА_Номер квартиры').Set(el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString())


        # ПОЛЬЗОВАТЕЛЬСКИЕ СЕМЕЙСТВА И СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ КОРОБОВ И КАБЕЛЬНЫХ ЛОТКОВ
        if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Номер квартиры'):
            # если не полоса заземления, категория пожарная сигнализация
            if el.Category.Id.IntegerValue != -2008085:
                # соединительные детали кабельных лотков и соединительные детали коробов тоже здесь
                # если семейство не вложенное
                if el.SuperComponent is None:
                    if el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString():
                        if el.LookupParameter('БУДОВА_Номер квартиры').AsString() is None or el.LookupParameter('БУДОВА_Номер квартиры').AsString() == "":
                            el.LookupParameter('БУДОВА_Номер квартиры').Set(el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString())

    t.Commit()


# # ИЗ НОМЕР КВАРТИРЫ В КОММЕНТАРИИ
# multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))
# with DB.Transaction(doc, 'comment_to_room') as t:
#     t.Start()
#     for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():

#         # КОРОБА И КАБЕЛЬНЫЕ ЛОТКИ
#         # у соед.деталей коробов и кабельных лотков нет параметра Уровень спецификации, а есть параметр Базовый уровень
#         # потому нужна отдельная обработка
#         # если выполняется любое из условий (аналогично функция all - выполняются все условия)
#         if any([
#             isinstance(el, DB.Electrical.Conduit),
#             isinstance(el, DB.Electrical.CableTray)
#             ]):
#             if el.LookupParameter('БУДОВА_Номер квартиры').AsString():
#                 if el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString() is None or el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString() == "":
#                     el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].Set(el.LookupParameter('БУДОВА_Номер квартиры').AsString())


#         # ПОЛЬЗОВАТЕЛЬСКИЕ СЕМЕЙСТВА И СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ КОРОБОВ И КАБЕЛЬНЫХ ЛОТКОВ
#         if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Номер квартиры'):
#             # если не полоса заземления, категория пожарная сигнализация
#             if el.Category.Id.IntegerValue != -2008085:
#                 # соединительные детали кабельных лотков и соединительные детали коробов тоже здесь
#                 # если семейство не вложенное
#                 if el.SuperComponent is None:
#                     if el.LookupParameter('БУДОВА_Номер квартиры').AsString():
#                         if el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString() is None or el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].AsString() == "":
#                             el.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS].Set(el.LookupParameter('БУДОВА_Номер квартиры').AsString())

#     t.Commit()




# with DB.Transaction(doc, 'comment_to_room') as t:
#     t.Start()
#     for el_circu in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit):
#         # УРОВНИ ПАНЕЛЕЙ
#         baseEquip = el_circu.BaseEquipment
#         # если цепь подключена, иначе у None нет атрибута Host
#         if baseEquip:
#             circParamNumber = el_circu.LookupParameter('БУДОВА_Номер квартиры')
#             circParamComment = el_circu.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS]

#             baseEqParamNumber = baseEquip.LookupParameter('БУДОВА_Номер квартиры')
#             baseEqParamComment = baseEquip.Parameter[DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS]

#             if circParamNumber.AsString() is None or circParamNumber.AsString() == "":
#                 circParamNumber.Set(baseEqParamNumber.AsString())

#     t.Commit()