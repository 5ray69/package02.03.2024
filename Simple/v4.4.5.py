# module v4.4.5.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

from selections import get_link_data
from geometry.functions import create_direct_shape

uiapp = __revit__                          # noqa
app = __revit__.Application                # noqa
uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa

# Получаем словарь данных связи
link_data = get_link_data(doc, 'Bathhouse_ARCH')
# Получаем элемент, в локации которого расположим direct_shape
element = link_data['doc'].GetElement(DB.ElementId(284492))
# Получаем трансформацию связи и применяем ее к точке
location = link_data['transforms'][0].OfPoint(element.Location.Point)
# Создаем direct_shape
create_direct_shape(doc, DB.Point.Create(location))
# # Создаем direct_shape в начале координат
# create_direct_shape(doc, DB.Point.Create(DB.XYZ.Zero))
