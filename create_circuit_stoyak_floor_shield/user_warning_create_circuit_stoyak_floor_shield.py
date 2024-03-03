# -*- coding: utf-8 -*-
# module user_warning_create_circuit_stoyak_floor_shield.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorActiveView(Exception):
    def __init__(self):
        self.message = "Активный вид не является разрезом.\
                        \nВыделите с помощью разреза этажные щиты\
                        \nдля создания электрических цепей стояков.\
                        \nПерейдите на вид разреза, щелкните левой кнопкой\
                        \nмыши на виде разреза и тогда запустите скрипт.\
                        \nСкрипт рабоает на вид разреза."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorSizeSectionView(Exception):
    def __init__(self, equipment, elementId):
        self.message = "Уменьшите ширину разреза так,\
                        \nчтобы он захватывал только те дозы, \
                        \n между которыми строятся стояки. \
                        \nСейчас попадает в разрез \
                        \n" + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nc имя панели: " + equipment.Name + ",\
                        \nc Id дозы: " + str(elementId.IntegerValue) + ",\
                        \nc уровень: " + equipment.Host.Name + ".\
                        \nЭто приведет к циклической ссылке. \
                        \nРевит видит семейства не так как пользователь,\
                        \nвозможно попадание невидимых для пользователя\
                        \nчастей элемента в границы разреза.\
                        \nУменьшите ширину разреза и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorCancelButton(Exception):
    def __init__(self):
        self.message = "Действие скрипта отменено.\
                        \nЭлектрические цепи стояков не построены."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorEmptyParamGroup(Exception):
    def __init__(self, el, levCond, elementId):
        self.message = "Параметр 'БУДОВА_Группа' не заполнен\
                        \nу элемента: " + el.Category.Name + ",\
                        \nc Id: " + str(elementId.IntegerValue) + ".\
                        \nПривязан к уровню: " + levCond + ".\
                        \nЗаполните параметр и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorEmptyStyleConduit(Exception):
    def __init__(self, el, levCond, elementId):
        self.message = "Параметр 'Стиль коробов' не заполнен\
                        \nу элемента: " + el.Category.Name + ",\
                        \nc Id: " + str(elementId.IntegerValue) + ".\
                        \nПривязан к уровню: " + levCond + ".\
                        \nЗаполните параметр и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)
