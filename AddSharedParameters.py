# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference("RevitAPIUI")
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB, UI
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

# from selections import get_element_by_name
# from application import close_inactive_docs, get_external_definition
# from document import FamilyLoadOptions

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo


# Класс указывающий программе что делать, если мы загружаем семейство
# в проект, а оно там уже существует
    # или возвращаем обратно семейство после изменений в исходный документ Ревита
    # f_doc.LoadFamily(doc, FamilyLoadOptions())  # значения параметров перезаписываются
    # f_doc.LoadFamily(doc, FamilyLoadOptions(False))  # значения параметров не перезаписываются
class FamilyLoadOptions(DB.IFamilyLoadOptions):
    def __init__(self, overwrite_parameters=True):
        super(FamilyLoadOptions, self).__init__()
        self._overwrite_parameters = overwrite_parameters

    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues.Value = self._overwrite_parameters
        return True


def close_inactive_docs(uiapp, save_modified=False, close_ui_docs=False):
    '''
    Закрыть все документы Revit, кроме текущего активного.
    save_modified - сохранять изменения в файлах
    close_ui_docs - закрывать документы, открытые в пользовательском интерфейсе (close_ui_docs=True)
    то есть при close_ui_docs=True закроются все открые нами документы, кроме активного
        (по умолчанию закрываются только документы, открытые в фоновом режиме (close_ui_docs=False))
    '''
    # перебераем по очереди все открытые документы revit
    for doc in uiapp.Application.Documents:
        # если это не текущий открытый в польз интерфесе документ
        if doc != uiapp.ActiveUIDocument.Document:
            # если это не связанный файл
            if doc.IsLinked:
                if not close_ui_docs and UI.UIDocument(doc).GetOpenUIViews():
                    continue
                name = doc.Title
                doc.Close(save_modified)
                # print 'Closed: {}'.format(name)

# пример закрытия всех открытых документов в фоновом режиме
# close_inactive_docs(uiapp)

categoriesId = [
    DB.ElementId(DB.BuiltInCategory.OST_ElectricalFixtures),  # эл.приборы
    DB.ElementId(DB.BuiltInCategory.OST_ElectricalEquipment),  # электрооборудование
    DB.ElementId(DB.BuiltInCategory.OST_LightingDevices),  # выключатели
    DB.ElementId(DB.BuiltInCategory.OST_LightingFixtures),  # осветительные приборы
    DB.ElementId(DB.BuiltInCategory.OST_Conduit),  # коробоа
    DB.ElementId(DB.BuiltInCategory.OST_ConduitFitting),  # соед.детали коробов
    DB.ElementId(DB.BuiltInCategory.OST_CableTrayFitting),  # соед.детали кабельных лотков
    DB.ElementId(DB.BuiltInCategory.OST_ElectricalCircuit),  # электрические цепи
    DB.ElementId(DB.BuiltInCategory.OST_FireAlarmDevices)  # пожарная сигнализация (заземление)
]

# ['Имя добавляемого параметра', 'Имя группы параметров из ФОП', True если экземпляр(иначе False)]
# не забывай ставить запятые между списками списков
addParams = [
    ['БУДОВА_Группа', 'БУДОВА_01. Универсальные параметры', True],
    ['БУДОВА_Наименование системы', 'БУДОВА_08. ОВиВК - Основные', True],
    ['БУДОВА_Захватка', 'БУДОВА_01. Универсальные параметры', True],
    ['БУДОВА_Этаж', 'БУДОВА_01. Универсальные параметры', True],
    ['БУДОВА_Номер квартиры', 'БУДОВА_05. АР - Помещения', True]
]

# Все семейства имеющиеся в диспетчере проекта указанных выше категорий
familys = [family for family in FEC(doc).OfClass(DB.Family) if family.FamilyCategoryId in categoriesId]
# oneFamily = [family for family in familys
#                                 if "Лампа накаливания" in family.Name]
for oneFamily in familys:
    f_doc = doc.EditFamily(oneFamily)
    # f_doc = doc.EditFamily(oneFamily[0])   # если выбрали одно семейство по имени

    with DB.Transaction(f_doc, 'add_parameter_in_family') as t:
        t.Start()
        f_manager = f_doc.FamilyManager
        # имена существующих параметров в семействе
        allFParams = [fparam.Definition.Name for fparam in f_manager.GetParameters()]

        # добавляем по одному общему! параметру если его нет в семействе
        for i in range(len(addParams)):
            if addParams[i][0] not in allFParams:
                f_manager.AddParameter(
                    app.OpenSharedParameterFile().Groups[addParams[i][1]].Definitions[addParams[i][0]],  # ExternalDefinition
                    DB.BuiltInParameterGroup.PG_TEXT,  # группа параметров семейства Текст
                    addParams[i][2]  # True = параметр экземляра
                )
            # возвращаем обратно после изменений обратно в исходный документ Ревита
            # FamilyLoadOptions() = значения параметров перезаписываются; FamilyLoadOptions(False) = не перезаписываются
        t.Commit()
    f_doc.LoadFamily(doc, FamilyLoadOptions())
    close_inactive_docs(uiapp)
























































# doc = DM.Instance.CurrentDBDocument
# family = [family for family in FEC(doc).OfClass(DB.Family) if "Щит этажный" in family.Name][0]
# f_doc = doc.EditFamily(family)
# # если галка Общий не стоит, то выдаст 0
# OUT = f_doc.OwnerFamily.Parameter[DB.BuiltInParameter.FAMILY_SHARED].AsInteger()







# # module v4.5.5.py
# # -*- coding: utf-8 -*-
# import clr
# clr.AddReference('RevitAPI')
# from Autodesk.Revit import DB
# from Autodesk.Revit.DB import FilteredElementCollector as FEC

# import sys
# sys.path += [
#     r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
# ]

# from selections import get_element_by_name
# from document import FamilyLoadOptions
# from application import close_inactive_docs

# uiapp = __revit__                          # noqa
# app = __revit__.Application                # noqa
# uidoc = __revit__.ActiveUIDocument         # noqa
# doc = __revit__.ActiveUIDocument.Document  # noqa

# # Обрабатываем только одно семейство, семейство дверей 'M_Single-Flush'
# # открываем семейство в виде отдельного документа:
# f_doc = doc.EditFamily(get_element_by_name(doc, 'M_Single-Flush', DB.Family))
# # свойство позволит взаимодествовать с параметрами
# # в таблице типоразмеров в семействе:
# f_manager = f_doc.FamilyManager

# # with DB.Transaction(f_doc, 'Set Family Shareds') as t:
# #     t.Start()
# #     # любой документ имеет свойство OwnerFamily и если это документ семейства,
# #     # то возвращает семейство, получаем из семейства параметр элемента (не таблицы типоразмеров) по перечислению
# #     f_doc.OwnerFamily.Prameter[DB.BuiltInParameter.FAMILY_SHARED].Set(1)
# #     t.Commit()

# # разорвать связь параметров (связь параметра элемента
# # с параметром проекта - связанные параметры)
# with DB.Transaction(f_doc, 'Disassosiate Parameters') as t:
#     t.Start()
#     # через коллектор перебираем все геометрические объекты
#     for g_element in FEC(f_doc).OfClass(DB.GenericForm):
#         # для каждого отдельного геометрического объекта
#         # перебираем все параметры данного элемента
#         for parameter in g_element.Parameters:
#             # проверяем не связан ли какой либо параметр семества с параметром элемента
#             f_parameter = f_manager.GetAssociatedFamilyParameter(parameter)
#             # если параметр связан
#             if f_parameter:
#                 # разрываем связь вместо параметра для связи None
#                 f_manager.AssociateElementParameterToFamilyParameter(
#                     parameter, None
#                 )

#     # любой документ имеет свойство OwnerFamily и если это документ семейства,
#     # то возвращает семейство, получаем из семейства параметр элемента (не таблицы типоразмеров) по перечислению
#     f_doc.OwnerFamily.Prameter[DB.BuiltInParameter.FAMILY_SHARED].Set(1)
#     t.Commit()

# f_doc.LoadFamily(doc, FamilyLoadOptions())
# close_inactive_docs(uiapp)
