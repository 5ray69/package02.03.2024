# -*- coding: utf-8 -*
# module without_create_shem_PIcosf.py
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


from create_shem_PIcosf.user_warning_create_shem_PIcosf import ErrorActiveView, \
                                                            ErrorNotHaveParameterNumberPanel, \
                                                            ErrorParameterNumberPanelNotValue, \
                                                            ErrorUserNoSelect
from create_shem_PIcosf.all_elements_panel_shem_PIcosf import AllElementsPanel
from create_shem_PIcosf.user_form_select_panel_number_shem_PIcosf import UserFormSelectPanelNumber


doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo

activeViewDrafting = doc.ActiveView

if not isinstance(activeViewDrafting, DB.ViewDrafting):
    raise ErrorActiveView()

categories = [
    DB.BuiltInCategory.OST_GenericAnnotation  # типовые аннотации
]

multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))

listNameFamily = [
    'BDV_E000_Схемы линия силовая',
    'BDV_E000_Схемы линия дымоудаления',
    'BDV_E000_Схемы линия квартир',
    'BDV_E000_Схемы линия офисов',
    'BDV_E000_Схемы линия освещения',
    'BDV_E000_Схемы линия освещения резерв',
    'BDV_E000_Схемы линия другой секции'
    ]

listFamilySymbol = [familySymbol for familySymbol in FEC(doc).OfClass(DB.FamilySymbol) \
        if familySymbol.Parameter[
            DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == 'BDV_E000_Схемы PIcosf секции']

OUT = []
with DB.Transaction(doc, 'create_shem_PIcosf') as t:
    t.Start()
    dictElements = {}
    # попадет в выборку только то что размещено на активном виде
    for el in FEC(doc, activeViewDrafting.Id).WherePasses(multicategory_filter).WhereElementIsNotElementType():
        if el.Symbol.Family.Name in listNameFamily:
            paramNumber = el.LookupParameter('БУДОВА_Номер панели')

            if not paramNumber:
                raise ErrorNotHaveParameterNumberPanel(el)
            # any интересуется значениями True и
            # возвращает True, находя первое из них,
            # или False — если не нашла ни одного

            if any([
                paramNumber.AsInteger() == "",
                paramNumber.AsInteger() is None,
                paramNumber.AsInteger() <= 0
                ]):
                raise ErrorParameterNumberPanelNotValue(el)

            if str(paramNumber.AsInteger()) not in dictElements:
                dictElements[str(paramNumber.AsInteger())] = []
            dictElements[str(paramNumber.AsInteger())].append(el)

    # строки перевели в числа отсортировали и перевели в строки
    listKey = [str(strKey) for strKey in sorted([int(key) for key in dictElements.keys()])]

    userFormSelectPanelNumber = UserFormSelectPanelNumber(listKey)
    userFormSelectPanelNumber.ShowDialog()
    # ЕСЛИ ПОЛЬЗОВАТЕЛЬ НИЧЕГО НЕ ВЫБРАЛ
    if not userFormSelectPanelNumber.listUserSelect:
        raise ErrorUserNoSelect()

    # ИЗ ВЫБРАННЫХ ПОЛЬЗОВАТЕЛЕМ ПАНЕЛЕЙ
    for key in userFormSelectPanelNumber.listUserSelect:
        family_ = doc.Create.NewFamilyInstance(
                            AllElementsPanel(dictElements[key]).getLocationXYZ(),
                            listFamilySymbol[0],
                            activeViewDrafting
                            )

        family_.LookupParameter('BDV_E000_Активная мощность панели кВт').Set(
                        AllElementsPanel(dictElements[key]).getActivPowerSum())
        family_.LookupParameter('BDV_E000_Полная мощность панели кВА').Set(
                        AllElementsPanel(dictElements[key]).getApparentPowerSum())

        family_.LookupParameter('BDV_E000_Ток по наиболее загруженной фазе').Set(
                        AllElementsPanel(dictElements[key]).getTokFromMaxFaz())

        family_.LookupParameter('BDV_E000_Ток в фазе А').Set(
                        AllElementsPanel(dictElements[key]).getTokFazaA())
        family_.LookupParameter('BDV_E000_Ток в фазе В').Set(
                        AllElementsPanel(dictElements[key]).getTokFazaB())
        family_.LookupParameter('BDV_E000_Ток в фазе С').Set(
                        AllElementsPanel(dictElements[key]).getTokFazaC())

        family_.LookupParameter('BDV_E000_отношение токов фаз A и B %').Set(
                        AllElementsPanel(dictElements[key]).getAsymmetryTokFazAB())
        family_.LookupParameter('BDV_E000_отношение токов фаз A и C %').Set(
                        AllElementsPanel(dictElements[key]).getAsymmetryTokFazAC())
        family_.LookupParameter('BDV_E000_отношение токов фаз B и C %').Set(
                        AllElementsPanel(dictElements[key]).getAsymmetryTokFazBC())

        family_.LookupParameter('БУДОВА_Номер панели').Set(int(key))

    t.Commit()

