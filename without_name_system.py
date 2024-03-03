# -*- coding: utf-8 -*
# module name_system.py
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
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo

with DB.Transaction(doc, 'NameSystem') as t:
    t.Start()
    circuit = []
    # категория Электрические цепи
    for el_circu in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
        NameSystem = el_circu.LookupParameter('БУДОВА_Наименование системы').AsString()

        # получаем нагрузку цепи
        for faminstan in el_circu.Elements:
            faminstan.LookupParameter('БУДОВА_Наименование системы').Set(NameSystem)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # СДЕЛАЙ ДЛЯ ЗАПИСИ НАИМЕНОВАНИЯ СИСТЕМЫ В КОРОБА МЕЖЭТАЖНЫХ ПЕРЕХОДОВ,
    # МЕТАЛЛОРУКАВА, КОРОБА ВЕНТИЛЯТОРОВ НА КРОВЛИ, НАСОСНУЮ И Т.Д. ЕСЛИ
    # БУДОВА ГРУППА СОВПАДАЕТ, ТО ЗАПИСЫВАЕМ ИЗ ЭЛ.ЦЕПИ В КОРОБ НАИМЕНОВАНИЕ СИСТЕМЫ
    # ЕСЛИ В ЦЕПИ ПУСТАЯ СТРОКА, ТО НЕ ЗАПИСЫВАЕМ НИЧЕГО

    t.Commit()
