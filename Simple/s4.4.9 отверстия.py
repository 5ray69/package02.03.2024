# module v4.4.6.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC


import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

from revitutils.unit import Unit
from selections import get_link_data
from geometry.functions import create_direct_shape

uiapp = __revit__                          # noqa
app = __revit__.Application                # noqa
uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa


#  свойство .IncludeNonVisibleObjects для получения скрытой геометрии
g_options = DB.Options()
g_options.IncludeNonVisibleObjects = True  # чтоб изменить свойство нужно использовать оператор присваивания (знак равно) присвоили свойству значение труе

# отбираем поверхности расположенные по середине стен
center_planar_face = {}
for wall in FEC(doc).OfClass(DB.Wall):
    # Перебираем солиды скрытых элементов
    for solid in wall.Geometry[g_options]:
        # получили FaceArray из солида
        for planar_face in solid.Faces:
            # Проверяем на пересечение поверхности и линии размещения стены на значение
            # подмножество (Subset). Линия размещения всегда по центру при любых настройках
            if planar_face.Intersect(wall.Location.Curve) == DB.SetComparisonResult.Subset:
                # Отбираем только вертикальные поверхности
                if not (planar_face.XVector.Z == 0 and planar_face.YVector.Z == 0):
                    # сколько бы ни было поверхностей в словаре окажется только одна из них
                    center_planar_face[wall] = planar_face

# получили трансформацию из экземпляра связи
mep_link_data = get_link_data(doc, 'IronPython_4408_Q_Intersection')
# к линии размещения воздуховодов применили трансформацию из экземпляра связи
# чтобы получить размещение линий в координатах основного файла
duct_curves = [
    duct.Location.Curve
    .CreateTransformed(mep_link_data['instances'][0].GetTotalTransform())
    for duct in FEC(mep_link_data['doc']).OfClass(DB.Mechanical.Duct)
]

# типизированная переменная
result_2 = clr.Reference[DB.IntersectionResultArray]()

# создали словарь стен с точками пересечений
wall_xyz = {}
for key, value in center_planar_face.items():
    for duct_curve in duct_curves:
        # проеверяем на пересечение поверхности и линии (Overlap - пересекается)
        if value.Intersect(duct_curve, result_2) == DB.SetComparisonResult.Overlap:
            if key not in wall_xyz:
                wall_xyz[key] = []
            wall_xyz[key].append(result_2.Item[0].XYZPoint)

# выбираем нужный типоразмер из обобщенных моделей
famil_types = [
    famil_type for famil_type in FEC(doc).OfCategory(
        DB.BuiltInCategory.OST_GenericModel).WhereElementIsElementType()
    if famil_type.Parameter[
        DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == '600x300'
]

difference = []
with DB.Transaction(doc, 'create holy') as t:
    t.Start()
    for wal, list_xyz in wall_xyz.items():
        for xyz in list_xyz:
            print(wal.Id)
            before = wal.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED].AsDouble()
            # пространство имен Autodesk.Revit.Creation.Document(класс Create)
            holy = doc.Create.NewFamilyInstance(
                xyz,
                famil_types[0],
                wal,
                doc.GetElement(wal.LevelId),
                DB.Structure.StructuralType.NonStructural
            )
            # установка параметра "Отметка от уровня" чтоб под воздуховод
            wal.WallType.Parameter[
            DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsDouble()
            holy.Parameter[DB.BuiltInParameter.INSTANCE_ELEVATION_PARAM].Set(
                xyz.Z - doc.GetElement(wal.LevelId).Elevation - Unit(doc, 150).internal)
            # регенерация модели
            doc.Regenerate()
            after = wal.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED].AsDouble()
            # если разность не равна нулю, то объем вырезается
            print(before - after)
            difference.append(before - after)
    t.Commit()

# объем всех стен после вырезания отверстий
wall_volume_after = []
for wall in FEC(doc).OfClass(DB.Wall):
    wall_volume_after.append(wall.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED].AsDouble())

print(round(Unit(doc, sum(wall_volume_after), False, DB.SpecTypeId.Volume).display, 2))



# start_xyz = wall.Location.Curve.GetEndPoint(0)
# end_xyz = wall.Location.Curve.GetEndPoint(1)
# # создаем вектор вычтя объекты XYZ один из другого
# v = end_xyz - start_xyz

# # создаем трансформацию смещения на 500мм по оси Z
# transform = DB.Transform.CreateTranslation(DB.XYZ(0, 0, Unit(doc, 500).internal))
# # создали точку, взяв центр Location.Curve стены, переместив объект xyz на 500мм по оси Z
# point = DB.Point.Create(transform.OfPoint(wall.Location.Curve.Evaluate(0.5, True)))

# Проецирует указанную точку на эту кривую
# Curve.Project(XYZ)

# Возвращает расстояние от этой точки до указанной точки
# XYZ.DistanceTo(XYZ)

# Вычисляет пересечение этой кривой с указанной кривой.
# Line.Intersect(Curve)

# Проецируем точку на плоскость и определяем расстояние до плоскости
# если точка лежит на плоскости, то расстояние до не равно нулю
# face.Project(Point).Distance

# face.Intersect(wall.Location.Curve)
# Subset - подмножество (Оба набора не пусты, и левый набор является строгим подмножеством правого набора)
# Disjoint - несвязный (Оба набора не пусты и не перекрываются)
# Overlap - наложение (Перекрытие двух наборов не является пустым и строгим подмножеством обоих наборов)

# HostObjectUtils.GetSideFaces(wall, ShellLayerType.Exterior) получение наружной грани

# Чтобы в python заработал метод Face.Intersect(Curve, IntersectionResultArray)
# resultArray = clr.Reference[DB.IntersectionResultArray]()
# face.Intersect(wall.Location.Curve, resultArray)

# Кривая расположения стены и общая толщина стены:
# wall.Location (объект LocationCurve)
# wall.WallType.Width (объект double)

# Итак, вы хотите увидеть, находится ли определенная точка на поверхности или нет?
# В этом случае вы можете просто использовать метод Face.Project(). Если он
#  возвращает null, это означает, что точка точно не на грани. В противном
#  случае сравните результат проекции и исходную точку, если они совпадают,
#  это означает, что исходная точка находится на грани.
