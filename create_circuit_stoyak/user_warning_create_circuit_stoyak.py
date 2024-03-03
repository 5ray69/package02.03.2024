# -*- coding: utf-8 -*-
# module user_warning_rename_circuit.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorActiveView(Exception):
    def __init__(self):
        self.message = "Активный вид не является разрезом.\
                        \nВыделите с помощью разреза соединительные\
                        \nкоробки (дозы) для создания стояков освещения.\
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


class ErrorNotIsPanelСonnection(Exception):
    def __init__(self, name):
        self.message = "Объект с именем:\
                        \n   " + "''" + name + "''" + " \
                        \nотсутствует в проекте.\
                        \nРазместите соответствующее семейство\
                        \nв электрощитовой, и запустите скрипт заново."
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
