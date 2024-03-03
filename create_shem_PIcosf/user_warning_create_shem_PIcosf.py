# -*- coding: utf-8 -*-
# module user_warning_create_shem_PIcosf.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorActiveView(Exception):
    def __init__(self):
        self.message = "Активный вид не является чертежным видом.\
                        \n\
                        \nСкрипт считывает семейства с чертежного вида и\
                        \nразмещает семейства на этом же чертежном виде.\
                        \n\
                        \nПерейдите на чертежный вид, щелкните на чертежном виде\
                        \nлевой кнопкой мыши и тогда запустите скрипт."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorMultiplePhases(Exception):
    def __init__(self, el):
        self.message = "Поставлены галки сразу у нескольких фаз\
                        \nпри напряжении 220В в семействе:\
                        \n\
                        \n" + el.Symbol.Family.Name + ",\
                        \n\
                        \nс типоразмером: " + el.Name + ",\
                        \n\
                        \nc Id: " + str(el.Id.IntegerValue) + "\
                        \n\
                        \nУберите лишние галки в семействе и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorSetPhasesIn380(Exception):
    def __init__(self, el):
        self.message = "Поставлена галка фазы\
                        \nпри напряжении 380В в семействе:\
                        \n\
                        \n" + el.Symbol.Family.Name + ",\
                        \n\
                        \nс типоразмером: " + el.Name + ",\
                        \n\
                        \nc Id: " + str(el.Id.IntegerValue) + "\
                        \n\
                        \nУберите все галки у фазы А, фазы B и фазы C\
                        \nи запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorCosIsNull(Exception):
    def __init__(self, el):
        self.message = "BDV_E000_cosφ равен нулю в семействе:\
                        \n\
                        \n" + el.Symbol.Family.Name + ",\
                        \n\
                        \nс типоразмером: " + el.Name + ",\
                        \n\
                        \nc Id: " + str(el.Id.IntegerValue) + "\
                        \n\
                        \nУстановите значение BDV_E000_cosφ отличное от нуля\
                        \nи запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorNotHaveParameterNumberPanel(Exception):
    def __init__(self, el):
        self.message = "Отсутствует параметр \
                        \n'БУДОВА_Номер панели' в семействе:\
                        \n\
                        \n" + el.Symbol.Family.Name + ",\
                        \n\
                        \nс типоразмером: " + el.Name + ",\
                        \n\
                        \nc Id: " + str(el.Id.IntegerValue) + "\
                        \n\
                        \nИли удалите это семейство из проекта.\
                        \nИли добавьте в это семейство этот парметр.\
                        \nИли обратитесь к координатору.\
                        \nПосле этого можно будет запустить скрпит заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorParameterNumberPanelNotValue(Exception):
    def __init__(self, el):
        self.message = "Параметр 'БУДОВА_Номер панели' \
                        \n либо меньше нуля, \
                        \n либо равен нулю,\
                        \n либо не заполнен\
                        \n\
                        \nв семействе:\
                        \n" + el.Symbol.Family.Name + ",\
                        \n\
                        \nс типоразмером: \
                        \n" + el.Name + ",\
                        \n\
                        \nc Id: \
                        \n" + str(el.Id.IntegerValue) + "\
                        \n\
                        \nЗаполните параметр соответствующим значением \
                        \nи запуститe скрпит заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorParameterPoweMissing(Exception):
    def __init__(self, el):
        self.message = "Параметр 'BDV_E000_Активная мощность кВт' \
                        \nотсутствует в семействе:\
                        \n" + el.Symbol.Family.Name + ",\
                        \n\
                        \nс типоразмером: \
                        \n" + el.Name + ",\
                        \n\
                        \nc Id: \
                        \n" + str(el.Id.IntegerValue) + "\
                        \n\
                        \nИли удалите это семейство из проекта.\
                        \nИли добавьте в это семейство этот парметр.\
                        \nИли обратитесь к координатору.\
                        \nПосле этого можно будет запустить скрпит заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorParameterTokMissing(Exception):
    def __init__(self, el):
        self.message = "Параметр 'BDV_E000_Iном' \
                        \nотсутствует в семействе:\
                        \n" + el.Symbol.Family.Name + ",\
                        \n\
                        \nс типоразмером: \
                        \n" + el.Name + ",\
                        \n\
                        \nc Id: \
                        \n" + str(el.Id.IntegerValue) + "\
                        \n\
                        \nИли удалите это семейство из проекта.\
                        \nИли добавьте в это семейство этот парметр.\
                        \nИли обратитесь к координатору.\
                        \nПосле этого можно будет запустить скрпит заново."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorUserNoSelect(Exception):
    def __init__(self):
        self.message = "Не выбран ни один номер панели.\
                        \nЗапустите скрипт заново и сделайте выбор.\
                        \n\
                        \nЕсли в списке нет ни одного номера панели,\
                        \nто вы не заполнили параметр БУДОВА_Номер панели\
                        \nу семейств линий подсоединенных к панелям.\
                        \nЗаполните параметр и запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)


































# class ErrorSizeSectionView(Exception):
#     def __init__(self, equipment, elementId):
#         self.message = "Уменьшите ширину разреза так,\
#                         \nчтобы он захватывал только те дозы, \
#                         \n между которыми строятся стояки. \
#                         \nСейчас попадает в разрез \
#                         \n" + equipment.Parameter[
#                                 DB.BuiltInParameter.ELEM_TYPE_PARAM].\
#                                 AsValueString() + ", \
#                         \nc имя панели: " + equipment.Name + ",\
#                         \nc Id дозы: " + str(elementId.IntegerValue) + ",\
#                         \nc уровень: " + equipment.Host.Name + ".\
#                         \nЭто приведет к циклической ссылке. \
#                         \nРевит видит семейства не так как пользователь,\
#                         \nвозможно попадание невидимых для пользователя\
#                         \nчастей элемента в границы разреза.\
#                         \nУменьшите ширину разреза и запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorCancelButton(Exception):
#     def __init__(self):
#         self.message = "Действие скрипта отменено.\
#                         \nЭлектрические цепи стояков не построены."
#         System.Windows.Forms.MessageBox.Show(self.message)


# class ErrorNotIsPanelСonnection(Exception):
#     def __init__(self, name):
#         self.message = "Объект с именем:\
#                         \n   " + "''" + name + "''" + " \
#                         \nотсутствует в проекте.\
#                         \nРазместите соответствующее семейство\
#                         \nв электрощитовой, и запустите скрипт заново."
#         System.Windows.Forms.MessageBox.Show(self.message)
