# module_cable_tray_coer.py
# -*- coding: utf-8 -*-
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

from length_conduit.user_warning_length_conduit import ErrorEmptyParamGroup

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo


unitLengType = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()


# ОСНОСНАЯ ИДЕЯ СКРИПТА
# Универсальное правило для всех вариантов - делить длину соед.детали на количество ПОДКЛЮЧЕННЫХ соединтелей в соед.детали = у соед.детали полученной
# из короба меньше одного ПОДКЛЮЧЕННОГО соединителя не будет, потому деления на ноль не получится

# Универсальный алгоритм для всех вариантов:
# нужно анализировать ВСЕ соединители короба,
# если соединитель имеет соед.деталь, то добавляем ее длину деленную
# на количество ПОДКЛЮЧЕННЫХ в этой соед.детали соединителей,
# суммирая участки длин в промежуточную переменную для этого короба.
# Когда все соединители короба просуммировали в нее, тогда эту переменную складываем с реальной длиной и записываем в фиктивную

# Пример, если соед.деталь подключена с двух сторон коробами, то половина ее длины добавляется к одному коробу, 
# а другая ее половина к другому коробу
# если соед.деталь только с одной стороны короба, то вся ее длина добавляется к подключенному коробу
# если у короба нет соед.деталей, то длина соед.деталей равна нулю и в фиктивную записывается реальная длина

with DB.Transaction(doc, 'length_conduit') as t:
    t.Start()
    DictCondt = {}
    # КОРОБА
    key = 0
    for conduit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_Conduit).WhereElementIsNotElementType():

        levCond = doc.GetElement(conduit.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name
        if not conduit.LookupParameter('БУДОВА_Группа').AsString():
            raise ErrorEmptyParamGroup(conduit, levCond, conduit.Id)

        # реальная длина короба
        realLength = conduit.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()

        # cуммируем длины соед.деталей
        partLength = 0

        # получаем два коннектора короба, по одному с каждого конца
        for connector in conduit.ConnectorManager.Connectors:

            # Два варианта не подключенного ни к чему короба:
            # 1. AllRefs может содержать 1 коннектор содержащийся в этом же коробе и быть не подключен
            # 2. AllRefs.Size неподключенного короба может быть равно нулю, т.е. AllRefs не содержит коннекторов
            # если к коннектору короба есть подключение соед.детали
            if connector.AllRefs.Size > 0:
                # здесь два коннектора: один коннектор соед. детали и один коннектор короба
                condFit = [connect.Owner for connect in connector.AllRefs if connect.Owner.Id != connector.Owner.Id]
                if condFit:
                    fitLength = condFit[0].LookupParameter('BDV_E000_Длина линии по внешнему радиусу').AsDouble()
                    # все подключенные коннекторы соед.детали (рассчитано, что в будущем может быть тройник)
                    isConnected = len([connect.IsConnected for connect in condFit[0].MEPModel.ConnectorManager.Connectors \
                                        if connect.IsConnected is True])
                    partLength += fitLength / isConnected

        conduit.LookupParameter('БУДОВА_Количество_Фиктивное').Set(
            DB.UnitUtils.ConvertFromInternalUnits(realLength + partLength, unitLengType)
            )
    t.Commit()
