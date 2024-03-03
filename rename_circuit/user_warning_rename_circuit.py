# -*- coding: utf-8 -*-
# module user_warning_rename_circuit.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorCircuitNoConect(Exception):
    def __init__(self):
        self.message = "Есть цепи неподключенные к панелям.\
                        \nCмотрите выпадающий список\
                        \nиз нода Python Script From String."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorEnglishLetter(Exception):
    def __init__(self, name_group_str, elementId):
        self.message = "Закройте этот скрипт и запустите\
                        \nскрипт 078_09_replace_english_letter_in_equipment_and_circuit.dyn\
                        \nЕсть английские буквы вместо русских\
                        \nв именах групп электрооборудования и цепей.\
                        \nНапример, в " + name_group_str + " Id элемента: " + str(elementId.IntegerValue)
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorNumberStoyak(Exception):
    def __init__(self, equipment, elementId):
        self.message = "Параметр 'BDV_E000_Номер стояка' или не заполнен,\
                        \nили имеет значение больше двух.\
                        \nИсправьте его значение в \
                        \n" + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nс именем панели " + equipment.Name + ", \
                        \nc Id элемента: " + str(elementId.IntegerValue) + ".\
                        \nИ запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorEmptyParameter(Exception):
    def __init__(self, equipment, elementId):
        self.message = "Параметр 'BDV_E000_Номер стояка' отсутвтует\
                        \nв семействе: " + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nс именем панели " + equipment.Name + ", \
                        \nc Id элемента: " + str(elementId.IntegerValue) + ".\
                        \n \
                        \nЗамените семейство на то,\
                        \nв котором есть этот параметр,\
                        \nили создайте по образцу такой параметр в семействе \
                        \nи запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorOboznachenieCzepey(Exception):
    def __init__(self, equipment, elementId):
        self.message = "Параметр 'Обозначение цепей' не заполнен.\
                        \nЗаполните параметр у \
                        \n" + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nc Id элемента: " + str(elementId.IntegerValue) + ".\
                        \nc уровень: " + equipment.Host.Name + ".\
                        \nИ запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorEmptyPanelName(Exception):
    def __init__(self, equipment, elementId):
        self.message = "Параметр 'Имя панели' не заполнен.\
                        \nЗаполните параметр у \
                        \n" + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nc Id элемента: " + str(elementId.IntegerValue) + ".\
                        \nc уровень: " + equipment.Host.Name + ".\
                        \nИ запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorConnectEquipment(Exception):
    def __init__(self, equipment, elementId):
        self.message = "К щиту цепью подключаться должна\
                        \n только соединительная коробка\
                        \n или другой элемент категории Электрооборудование.\
                        \n Cветильники и розетки напрямую к щиту\
                        \n не должны быть подключены\
                        \n (только через соединительную коробку).\
                        \n Смотрите щит/панель: \
                        \n" + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nc Id элемента: " + str(elementId.IntegerValue) + ".\
                        \nc уровень: " + equipment.Host.Name + ".\
                        \nИсправьте подключения и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorNoneLevel(Exception):
    def __init__(self, element, elementId, levelName):
        self.message = "Элемент не привязан к уровню.\
                        \nСмотрите элемент: \
                        \n" + "   "  + element.Name + " \
                        \nc Id элемента: " + str(elementId.IntegerValue) + "\
                        \nнад уровнем: " + levelName + "\
                        \nВыберите уровень для элемента, \
                        \n c помощью <Редактировать рабочую плоскость>,\
                        \n и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorShieldLevelNotInUserForm(Exception):
    def __init__(self, equipment, elementId):
        self.message = "Щит расположен на уровне, который \
                        \nне предусмотрен в форме пользователя.\
                        \n \
                        \n Щит: " + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nс Id: " + str(elementId.IntegerValue) + ".\
                        \nc уровень: " + equipment.Host.Name + ".\
                        \n \
                        \nИли разместите щит на уровне жилых этажей/офисов, \
                        \nили обратитесь к координатору для изменения формы."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorElementNotInSchedule(Exception):
    def __init__(self, strNameSchedule, strNameElement):
        self.message = "Элемент с ключевым именем: " + strNameElement + "\
                        \n\
                        \nне найден в ключевой спецификации:\
                        \n " + strNameSchedule
        System.Windows.Forms.MessageBox.Show(self.message)
