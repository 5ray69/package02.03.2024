# module create_conduit_for_tech_level.py
# -*- coding: utf-8 -*

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

# "C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Разработка Варненская, 9\Скрипты\create_conduit_for_tech_level\user_form_create_conduit.py"
from revitutils.unit import Unit
from create_conduit_for_tech_level.user_form_create_conduit import UserFormCreateConduitForLevel, ErrorMessageViewNotConnectedToLevel
from create_conduit_for_tech_level.sort_names_levels_create_conduit import my_sort_names_levels

doc = DM.Instance.CurrentDBDocument  # Получение файла документа


levels_from_project = my_sort_names_levels([lev.Name for lev in FEC(doc).OfClass(DB.Level)])
form = UserFormCreateConduitForLevel(levels_from_project)
form.ShowDialog()
# список выбора пользователя
# В список помещаем имя уровня, для которого хотим создать из эл.цепей короба
level_selected_user = []
for el in form.list_user_select:
    if el == 'Активный вид':
        # если активный вид связан с уровнем
        if isinstance(doc.ActiveView, DB.ViewPlan):
            level_selected_user.append(doc.ActiveView.GenLevel.Name)
        else:
            ErrorMessageViewNotConnectedToLevel()
    else:
        level_selected_user.append(el)


# Получаем ElementId нужного типоразмера
conduitType_elementId = [con.Id for con in FEC(doc).OfClass(DB.Electrical.ConduitType) \
                        if con.Parameter[DB.BuiltInParameter.ALL_MODEL_FAMILY_NAME].AsString() == 'Короб с соединительными деталями' \
                        and con.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == 'Короб']


with DB.Transaction(doc, 'create_conduit_for_tech_level') as t:
    t.Start()
    for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
        if doc.GetElement(el_circuit.BaseEquipment.Id).Host.Name in level_selected_user:
            # Если калассификация нагрузок Id=8388542 (Автоматика теплых полов)
            if el_circuit.BaseEquipment.Symbol.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == 8388542:
                # к Приложению теплых полов витая пара идет открыто по стенам, без гофры
                # если Приложения нет в нагрузках цепи
                if [faminstan for faminstan in el_circuit.Elements if "Приложение" not in faminstan.Symbol.Family.Name]:
                    # получили путь/траекторию цепи
                    path = el_circuit.GetCircuitPath()
                    for i in range(len(path) - 1):
                        if path[i].DistanceTo(path[i + 1]) > 0.1:
                            conduit = DB.Electrical.Conduit.Create(
                                doc,
                                conduitType_elementId[0],
                                path[i],
                                path[i + 1],
                                # Id уровня дозы, к которой подключена цепь
                                doc.GetElement(el_circuit.BaseEquipment.Id).Host.Id
                            )
                            # получаем нагрузки цепи
                            # Диаметр Короба (Размер по каталогу)
                            # Присвоили коробу диаметр наружного диаметра кабеля, если его нет, то назначаем диаметр из списка каталога 9мм 
                            # если в каталоге такого диаметра нет, то все, внутренний, наружный и по каратлогу будут 9мм,
                            # если близок к имеющемуся, то будет выбран имеющийся из каталога)
                            conduit.Parameter[DB.BuiltInParameter.RBS_CONDUIT_DIAMETER_PARAM].Set(Unit(doc, 20).internal)
                            # присваиваем значение 'гофра 20мм' ElementId 8556335
                            conduit.LookupParameter('Стиль коробов').Set(DB.ElementId(8556335))

                            # БУДОВА_Группа
                            if el_circuit.LookupParameter('БУДОВА_Группа').AsString():
                                conduit.LookupParameter('БУДОВА_Группа').Set(
                                    el_circuit.LookupParameter('БУДОВА_Группа').AsString())
                            else:
                                conduit.LookupParameter('БУДОВА_Группа').Set('')
                            # conduits.append(conduit)

                            # БУДОВА_Уровень оборудования
                            if el_circuit.LookupParameter('БУДОВА_Уровень оборудования').AsString():
                                conduit.LookupParameter('БУДОВА_Уровень оборудования').Set(
                                    el_circuit.LookupParameter('БУДОВА_Уровень оборудования').AsString())
                            else:
                                conduit.LookupParameter('БУДОВА_Уровень оборудования').Set('')
                            # БУДОВА_Этаж
                            if el_circuit.LookupParameter('БУДОВА_Этаж').AsString():
                                conduit.LookupParameter('БУДОВА_Этаж').Set(
                                    el_circuit.LookupParameter('БУДОВА_Этаж').AsString())
                            else:
                                conduit.LookupParameter('БУДОВА_Этаж').Set('')
                            # БУДОВА_Классификация нагрузок
                            if el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue != -1:
                                conduit.LookupParameter('БУДОВА_Примечание').Set(
                                    doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name)

                            # БУДОВА_Номер квартиры
                            if el_circuit.LookupParameter('БУДОВА_Номер квартиры').AsString():
                                conduit.LookupParameter('БУДОВА_Номер квартиры').Set(
                                    el_circuit.LookupParameter('БУДОВА_Номер квартиры').AsString())
                            else:
                                conduit.LookupParameter('БУДОВА_Номер квартиры').Set('')

                            # BDV_E000_Имя помещения
                            if el_circuit.LookupParameter('BDV_E000_Имя помещения').AsString():
                                conduit.LookupParameter('BDV_E000_Имя помещения').Set(
                                    el_circuit.LookupParameter('BDV_E000_Имя помещения').AsString())
                            else:
                                conduit.LookupParameter('BDV_E000_Имя помещения').Set('')

                            # BDV_E000_Номер помещения
                            if el_circuit.LookupParameter('BDV_E000_Номер помещения').AsString():
                                conduit.LookupParameter('BDV_E000_Номер помещения').Set(
                                    el_circuit.LookupParameter('BDV_E000_Номер помещения').AsString())
                            else:
                                conduit.LookupParameter('BDV_E000_Номер помещения').Set('')

                            # БУДОВА_Наименование системы
                            if el_circuit.LookupParameter('БУДОВА_Наименование системы').AsString():
                                conduit.LookupParameter('БУДОВА_Наименование системы').Set(
                                    el_circuit.LookupParameter('БУДОВА_Наименование системы').AsString())
                            else:
                                conduit.LookupParameter('БУДОВА_Наименование системы').Set('')
    t.Commit()
