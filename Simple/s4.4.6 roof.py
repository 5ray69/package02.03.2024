# module v4.4.6.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

from revitutils.unit import Unit
from iterfunctions import flatten
from selections import get_link_data
from geometry.functions import create_direct_shape

uiapp = __revit__                          # noqa
app = __revit__.Application                # noqa
uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa

# Получаем словарь данных связи
link_data = get_link_data(doc, 'Bathhouse_ARCH')
# Получаем элемент, из которого получим точки и в них расположим direct_shape
roof = link_data['doc'].GetElement(DB.ElementId(284077))

# формируем словарь ключ - ребро, значение - сумма координат Z точек начала и конца ребра
lines = {}
for geometr in roof.Geometry[DB.Options()]:
    for edge in geometr.Edges:
        if edge not in lines:
            lines[edge] = edge.AsCurve().GetEndPoint(0).Z + edge.AsCurve().GetEndPoint(1).Z

# из словаря выбрали ребро с максимальной суммой координат Z
# (отсортировали словарь, ключ для сортировки - элемент с индексом 1 (value) и [0][0] получили ключ=ребро)
roof_ridge = sorted(lines.items(), key=lambda item: item[1])[-1:][0][0]
# Получаем трансформацию связи и применяем ее к точке
location_0 = link_data['transforms'][0].OfPoint(roof_ridge.AsCurve().GetEndPoint(0))
location_1 = link_data['transforms'][0].OfPoint(roof_ridge.AsCurve().GetEndPoint(1))
loc_sun = Unit(doc, location_0.X, False).display + Unit(doc, location_0.Y, False).display + Unit(doc, location_0.Z, False).display + Unit(doc, location_1.X, False).display + Unit(doc, location_1.Y, False).display + Unit(doc, location_1.Z, False).display
# loc_sun = location_0.X + location_0.Y + location_0.Z + location_1.X + location_1.Y + location_1.Z
print(location_0)
print(location_1)
print(loc_sun)
# print(Unit(doc, loc_sun, False).display)
# одинаково, что после суммирования ковертировать в мм, что складывать мм

# Создаем direct_shape
create_direct_shape(doc, DB.Point.Create(location_0))
create_direct_shape(doc, DB.Point.Create(location_1))
