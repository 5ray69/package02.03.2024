# -*- coding: utf-8 -*-
# module user_warning_in_room.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorThereAreNoLevels(Exception):
    def __init__(self, NotInList):
        self.message = "В основном файле отсутствуют уровни,\
                        \nкоторые есть в файле связи:\
                        \n" + ' ,'.join(NotInList) + ".\
                        \nОбратитесь к координатору для\
                        \nкопирования недостающих уровней из файла связи\
                        \nи после исправления ошибки запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorUserNoSelect(Exception):
    def __init__(self):
        self.message = "Не выбрано ни одно имя файла связи.\
                        \nЗапустите скрипт заново и сделайте выбор.\
                        \n\
                        \nЕсли в списке нет ни одного имени файла связи,\
                        \nа связь есть в проекте, то возможно связь выгужена.\
                        \n\
                        \nВ диспетчере на связи правой кнопкой мыши\
                        \nвыбираем Обновить и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorEmptyParameter(Exception):
    def __init__(self, el, elementId):
        self.message = "Параметр 'БУДОВА_Этаж' не заполнен\
                        \nу элемента \
                        \nс именем: " + el.Name + ", \
                        \nc Id элемента: " + str(elementId.IntegerValue) + ".\
                        \nЗлемент не привязан к уровню, размещен на грани. \
                        \nЗапустите скрипт fill_in_the_zahv_set \
                        \nИ запустите скрипт in_room заново."
        System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorNumberStoyak(Exception):
#     def __init__(self, equipment, elementId):
#         self.message = "Параметр 'BDV_E000_Номер стояка' или не заполнен,\
#                         \nили имеет значение больше двух.\
#                         \nИсправьте его значение в \
#                         \n" + equipment.Parameter[
#                                 DB.BuiltInParameter.ELEM_TYPE_PARAM].\
#                                 AsValueString() + ", \
#                         \nс именем панели " + equipment.Name + ", \
#                         \nc Id элемента: " + str(elementId.IntegerValue) + ".\
#                         \nИ запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorEmptyParameter(Exception):
#     def __init__(self, equipment, elementId):
#         self.message = "Параметр 'BDV_E000_Номер стояка' отсутвтует\
#                         \nв семействе: " + equipment.Parameter[
#                                 DB.BuiltInParameter.ELEM_TYPE_PARAM].\
#                                 AsValueString() + ", \
#                         \nс именем панели " + equipment.Name + ", \
#                         \nc Id элемента: " + str(elementId.IntegerValue) + ".\
#                         \n \
#                         \nЗамените семейство на то,\
#                         \nв котором есть этот параметр,\
#                         \nили создайте по образцу такой параметр в семействе \
#                         \nи запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorOboznachenieCzepey(Exception):
#     def __init__(self, equipment, elementId):
#         self.message = "Параметр 'Обозначение цепей' не заполнен.\
#                         \nЗаполните параметр у \
#                         \n" + equipment.Parameter[
#                                 DB.BuiltInParameter.ELEM_TYPE_PARAM].\
#                                 AsValueString() + ", \
#                         \nc Id элемента: " + str(elementId.IntegerValue) + ".\
#                         \nc уровень: " + equipment.Host.Name + ".\
#                         \nИ запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorEmptyPanelName(Exception):
#     def __init__(self, equipment, elementId):
#         self.message = "Параметр 'Имя панели' не заполнен.\
#                         \nЗаполните параметр у \
#                         \n" + equipment.Parameter[
#                                 DB.BuiltInParameter.ELEM_TYPE_PARAM].\
#                                 AsValueString() + ", \
#                         \nc Id элемента: " + str(elementId.IntegerValue) + ".\
#                         \nc уровень: " + equipment.Host.Name + ".\
#                         \nИ запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorConnectEquipment(Exception):
#     def __init__(self, equipment, elementId):
#         self.message = "К щиту цепью подключаться должна\
#                         \n только соединительная коробка\
#                         \n или другой элемент категории Электрооборудование.\
#                         \n Cветильники и розетки напрямую к щиту\
#                         \n не должны быть подключены\
#                         \n (только через соединительную коробку).\
#                         \n Смотрите щит/панель: \
#                         \n" + equipment.Parameter[
#                                 DB.BuiltInParameter.ELEM_TYPE_PARAM].\
#                                 AsValueString() + ", \
#                         \nc Id элемента: " + str(elementId.IntegerValue) + ".\
#                         \nc уровень: " + equipment.Host.Name + ".\
#                         \nИсправьте подключения и запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorNoneLevel(Exception):
#     def __init__(self, element, elementId, levelName):
#         self.message = "Элемент не привязан к уровню.\
#                         \nСмотрите элемент: \
#                         \n" + "   "  + element.Name + " \
#                         \nc Id элемента: " + str(elementId.IntegerValue) + "\
#                         \nнад уровнем: " + levelName + "\
#                         \nВыберите уровень для элемента, \
#                         \n c помощью <Редактировать рабочую плоскость>,\
#                         \n и запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorShieldLevelNotInUserForm(Exception):
#     def __init__(self, equipment, elementId):
#         self.message = "Щит расположен на уровне, который \
#                         \nне предусмотрен в форме пользователя.\
#                         \n \
#                         \n Щит: " + equipment.Parameter[
#                                 DB.BuiltInParameter.ELEM_TYPE_PARAM].\
#                                 AsValueString() + ", \
#                         \nс Id: " + str(elementId.IntegerValue) + ".\
#                         \nc уровень: " + equipment.Host.Name + ".\
#                         \n \
#                         \nИли разместите щит на уровне жилых этажей/офисов, \
#                         \nили обратитесь к координатору для изменения формы."
#         System.Windows.Forms.MessageBox.Show(self.message)
