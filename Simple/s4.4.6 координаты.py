# module s4.4.6 координаты.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
# clr.AddReference('RevitAPIUI')  # для Dynamo
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC

import os
import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

uiapp = __revit__                          # noqa
app = __revit__.Application                # noqa
uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa

# основное назначение создаваемого класса - дать понять программе,
# сохранять или нет общие координаты связанного файла при его выгрузке,
# если вдруг они были изменены.
class SaveSharedCoordinatesCallback(DB.ISaveSharedCoordinatesCallback):
    def __init__(self, save_options):
        super(SaveSharedCoordinatesCallback, self).__init__()
        self._save_options = save_options

    def GetSaveModifiedLinksOption(self, link):
        return self._save_options


# создаем экземпляр нового класса и используем его для выгрузки связей
callback = SaveSharedCoordinatesCallback(DB.SaveModifiedLinksOptions.SaveLinks)

# У всех объектов, размещенных не по общим координатам,
# в имени будет присутствовать строка "<Не общедоступное>"
# (в английской версии Revit - "<Not Shared>").
# В противном случае, после слова "позиция" будет указано имя площадки,
# на основе которой размещен экземпляр связи.
# Исходя из этого возникает два возможных варианта проверок имени экземпляра связи:
# -либо на наличие строки "<Не общедоступное>";
# -либо на отсутствие имени текущей активной площадки,
#   которое можно получить следующим образом: link_instance.GetLinkDocument().ActiveProjectLocation.Name.

# ВЫБОРКА ЭКЗЕМПЛЯРОВ СВЯЗЕЙ
# Словарь, ключами которого будут экземпляры необходимых нам связей, а значениями - их типоразмеры:
# отобираем связи размещенные не по общим координатам == <Не общедоступное>
link_elements = {
    link_instance: doc.GetElement(link_instance.GetTypeId())
    for link_instance in FEC(doc).OfClass(DB.RevitLinkInstance)
    if '<Не общедоступное>' in link_instance.Name
}

# ВЫГРУЖАЕМ И ЗАГРУЖАЕМ СВЯЗИ
# И теперь каждый связанный файл перед открытием будет выгружаться.
# И только после этого мы будем производить его изменение, закрывать 
# и перезагружать связь обратно в документ:
# перебираем словарь:
for link_instance, link_type in link_elements.items():
    # выгружаем связь с помощью экземлеяра созданного класса
    link_type.Unload(callback)
    # открываем выгруженную связь
    link_doc = app.OpenDocumentFile(
        link_type.GetExternalFileReference().GetAbsolutePath(),
        DB.OpenOptions()
    )
    # задаем имени площадки связанного файла точно такое же значение,
    # как и в основном, чтобы в дальнейшем понимать,
    # что мы имеем дело с одной и той же площадкой:
    with DB.Transaction(link_doc, 'Rename Project Location') as t:
        t.Start()
        link_doc.ActiveProjectLocation.Name = doc.ActiveProjectLocation.Name
        t.Commit()
    link_doc.Close()
    # перезагружаем связь обратно в файл
    link_type.Reload()

# передадим связям общие координаты из основного файла
with DB.Transaction(doc, 'Publish Coordinates') as t:
    t.Start()
    # перебираем словарь
    for link_instance, link_type in link_elements.items():
        doc.PublishCoordinates(
            DB.LinkElementId(
                link_instance.Id,
                link_instance.GetLinkDocument().ActiveProjectLocation.Id
            )
        )
        link_type.SavePositions(callback)
    t.Commit()







# ПЕРЕИМЕНОВЫВАЕМ ПЛОЩАДКИ
# Перед тем как переименовывать необходимо выгрузить связи, 
# потому код ниже выдаст ошибку. Код описан лишь для того,
# чтоб показать как переименовывается площадка
# по очереди открываем каждый документ связанного файла в фоновом режиме,
# изменяем имя текущей активной площадки и закрываем файл
# for link_instance, link_type in link_elements.items():
#     link_doc = app.OpenDocumentFile(
#         link_type.GetExternalFileReference().GetAbsolutePath(),
#         DB.OpenOptions()
#     )
#     with DB.Transaction(link_doc, 'Rename Project Location') as t:
#         t.Start()
#         link_doc.ActiveProjectLocation.Name = doc.ActiveProjectLocation.Name
#         t.Commit()
#     link_doc.Close()
