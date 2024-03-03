# module s4.4.3.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
# clr.AddReference('RevitAPIUI')  # для Dynamo
from Autodesk.Revit import DB
# импорт из пространства имен System.IO класса Directory и перечисления SearchOption
from System.IO import Directory, SearchOption

import os
import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

uiapp = __revit__                          # noqa
app = __revit__.Application                # noqa
uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa

directoryPath = r"D:\Андрей\7fold\4 Взаимодействие с различными элементами Revit\4.4 Работа со связанными файлами\4.4 Задачи\Файл для задачи 4.4.3\updat 3"
# Обновляем файлы до версии, ревит которой открыт. Открыт любой файл не из обновляемых.
# "*" - будет искать все файлы в папках
# "*.rfa" - будет искать все файлы семейств
# "*.rvt" - будет искать все файлы проектов
# "*.rte" - будет искать все файлы шаблонов
searchstring = "*.rvt"
# если заданный путь указывает на существующий каталог на диске
if Directory.Exists(directoryPath):
    # получаем имена файлов (включая пути) в заданном каталоге,
    # отвечающие условиям шаблона поиска, используя значение,
    # которое определяет, выполнять ли поиск в подкаталогах
    for pathfile in Directory.GetFiles(
                        directoryPath,
                        searchstring,
                        SearchOption.AllDirectories):
        # исключаем открытие файла с тем же именем, что и у текущего
        if [pathfile.find(doc.Title) == -1] and [pathfile.find('.rvt') == -1]:
            filedoc = app.OpenDocumentFile(pathfile)
for docum in app.Documents:
    if docum.Title != doc.Title:
        docum.Close(True)

with DB.Transaction(doc, 'LoadLink') as t:
    t.Start()
    if Directory.Exists(directoryPath):
        for pathfile in Directory.GetFiles(
                            directoryPath,
                            searchstring,
                            SearchOption.AllDirectories):
            # исключаем открытие файла с тем же именем, что и у текущего
            if [pathfile.find(doc.Title) == -1] and [pathfile.find('.rvt') == -1]:
                # Добавили типоразмеры связей, но файлов еще нет, файлы - это экземпляры
                load_result = DB.RevitLinkType.Create(
                    doc,
                    DB.ModelPathUtils.ConvertUserVisiblePathToModelPath(
                        pathfile
                    ),
                    DB.RevitLinkOptions(True)
                )
                revit_link_instance = DB.RevitLinkInstance.Create(
                    doc,
                    load_result.ElementId,
                    DB.ImportPlacement.Shared if 'Shared' in pathfile
                    else DB.ImportPlacement.Origin
                )
                print '{}: {}'.format(pathfile, load_result.LoadResult)
    t.Commit()
