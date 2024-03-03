# module v4.4.7.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

from selections import get_link_data
from geometry.functions import create_direct_shape
from iterfunctions import to_list
from geometry.functions import get_min_max
from geometry.boundingbox import BoundingBoxXYZExtended
from Autodesk.Revit.DB import Plumbing as PB  # для получения локаций труб

doc = __revit__.ActiveUIDocument.Document  # noqa

# получили трансформацию из экземпляра связи
arhc_link_data = get_link_data(doc, 'Bathhouse_ARCH')
transform = arhc_link_data['instances'][0].GetTotalTransform()

# получаем из связанного файла локации всех элементов категорий "Двери" и "Окна"

# в переменную locations попадут точки в системе координат связанного файла
locations = [
    element.Location.Point
    for element in FEC(arhc_link_data['doc']).WhereElementIsNotElementType()
    .WherePasses(
        DB.ElementMulticategoryFilter(
            to_list(
                [
                    DB.BuiltInCategory.OST_Windows,
                    DB.BuiltInCategory.OST_Doors,
                ],
                DB.BuiltInCategory
            )
        )
    )
]

# в переменную locations_transformed попадут точки в системе координат текущего файла
locations_transformed = [
    transform.OfPoint(location)
    for location in locations
]

# Создаем BoundingBox, НЕ учитывающий трансформацию экземпляра связи.
# Габариты ящика необходимо получать в системе координат связанного
# файла (т.е. на основе нетрансформированных точек), и только потом
# применять к нему трансформацию.

min_point, max_point = get_min_max(locations_transformed)
bounding_box = BoundingBoxXYZExtended()
bounding_box.Min = min_point
bounding_box.Max = max_point

min_point, max_point = get_min_max(locations)
bounding_box = BoundingBoxXYZExtended()
bounding_box.Min = min_point
bounding_box.Max = max_point
# применили трансформацию экземпляра связи
bounding_box.Transform = transform

# ПРОВЕРКА ГАБАРИТОВ И РАСПОЛОЖЕНИЯ ЯЩИКА
# Для визуальной проверки результатов создадим два объекта DirectShape.
# Один из них будет включать в себя все полученные точки.
# Другой - габаритный ящик, превращенный в объект класса Solid.
create_direct_shape(
    doc,
    [DB.Point.Create(location) for location in locations_transformed]
)

create_direct_shape(
    doc,
    bounding_box.solid
)

# ПОЛУЧЕНИЕ КРИВЫХ
# Механизм получения кривых из связанного файла схож с получением точек и отличается лишь методом,
# при помощи которого мы получаем трансформированную
# версию кривых (в данном случае это метод CreateTransformed класса Curve).
# В качестве примера получим все линии локации труб из файла Bathhouse_MEP.rvt:
mep_link_data = get_link_data(doc, 'Bathhouse_MEP')
pipe_curves = [
    pipe.Location.Curve
    .CreateTransformed(mep_link_data['instances'][0].GetTotalTransform())
    for pipe in FEC(mep_link_data['doc']).OfClass(PB.Pipe)
]
create_direct_shape(doc, pipe_curves)

# ПОЛУЧЕНИЕ ТВЕРДЫХ ТЕЛ
# Похоже на предыдущие примеры. Метод для получения трансформированного варианта твердого
# тела имеет то же название, но в данном случае он является статическим и относится к классу SolidUtils.

# В качестве примера получим объекты Solid для всех труб из файла Bathhouse_MEP.rvt:
solids = []
for pipe in FEC(mep_link_data['doc']).OfClass(PB.Pipe):
    for item in pipe.Geometry[DB.Options()]:
        if isinstance(item, DB.Solid):
            solids.append(
                DB.SolidUtils.CreateTransformed(
                    item,
                    mep_link_data['instances'][0].GetTotalTransform()
                )
            )
create_direct_shape(doc, solids)
