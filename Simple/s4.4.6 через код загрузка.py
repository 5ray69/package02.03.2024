# module s4.4.6 загрузка.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
# clr.AddReference('RevitAPIUI')  # для Dynamo
from Autodesk.Revit import DB

import os
import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

uiapp = __revit__                          # noqa
app = __revit__.Application                # noqa
uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa

# создали переменную, которая является строкой (полный путь к нашей папке)
directory_path = r"D:\Андрей\7fold\4 Взаимодействие с различными элементами Revit\4.4 Работа со связанными файлами\4.4 Задачи\Файл для задачи 4.4.5\для задачи неизмененный"
with DB.Transaction(doc, 'Add Revit Link') as t:
    t.Start()
    # получаем содержимое папки, в которой лежат связи
    # listdir возвращает как имена файлов так и папок
    # от версии Revit это не зависит вообще
    for item_name in os.listdir(directory_path):
        # исходное полное имя файла с расширением разбиваем на две строки
        # одна - имя, вторая - расширение
        name, extension = os.path.splitext(item_name)
        # doc.Title получаем имя текущего файла - так исключили текущий файл
        if name != doc.Title and extension == '.rvt':
            # Добавили типоразмеры связей, но файлов еще нет, файлы - это экземпляры
            load_result = DB.RevitLinkType.Create(
                doc,
                DB.ModelPathUtils.ConvertUserVisiblePathToModelPath(
                    os.path.join(directory_path, item_name)
                ),
                DB.RevitLinkOptions(True)
            )
            # Добавляем экземпляры связей
            revit_link_instance = DB.RevitLinkInstance.Create(
                doc,
                load_result.ElementId,
                DB.ImportPlacement.Shared  # .Shared - по общим координатам
            )
            print '{}: {}'.format(item_name, load_result.LoadResult)

    t.Commit()
