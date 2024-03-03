# -*- coding: utf-8 -*
# module all_elements_panel_shem_PIcosf.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


from create_shem_PIcosf.user_warning_create_shem_PIcosf import ErrorMultiplePhases, \
                                                                ErrorSetPhasesIn380, \
                                                                ErrorCosIsNull, \
                                                                ErrorParameterPoweMissing, \
                                                                ErrorParameterTokMissing

from create_shem_PIcosf.how_many_phases_create_shem_PIcosf import HowManyPhases


class AllElementsPanel(object):
    # в миллиметрах
    offsetForY = 2800
    
    def __init__(self, elements):
        self.elements = elements

        self.activPowFaz = self.getActivPowFaz()
        self.tokFaz = self.getTokFaz()
        self.apparentPowerSum = self.getApparentPowerSum()
        self.аctivPowerSum = self.getActivPowerSum()

        self.cosSum = self.getCosSum()
        self.tgSum = self.getTgSum()
        self.reаctivPowerSum = self.getReactivPowerSum()

        self.tokFazaA = self.getTokFazaA()
        self.tokFazaB = self.getTokFazaB()
        self.tokFazaC = self.getTokFazaC()

        self.tokFromMaxFaz = self.getTokFromMaxFaz()

        self.asymmetryTokFazAB = self.getAsymmetryTokFazAB()
        self.asymmetryTokFazBC = self.getAsymmetryTokFazBC()
        self.asymmetryTokFazAC = self.getAsymmetryTokFazAC()

        self.locationXYZ = self.getLocationXYZ()


    def getActivPowFaz(self):
        """словарь активной мощности,кВт всех элементов одной панели пофазно
        """

        activPowFaz = {"A": 0.0, "B": 0.0, "C": 0.0}

        for el in self.elements:
            paramPower = el.LookupParameter('BDV_E000_Активная мощность кВт')
            if not paramPower:
                raise ErrorParameterPoweMissing(el)

            activPow = paramPower.AsDouble()

            if el.LookupParameter('BDV_E000_220').AsInteger():
                # предупреждение, что включено больше одной фазы
                if HowManyPhases(el).getCount() > 1:
                    raise ErrorMultiplePhases(el)

                if el.LookupParameter('BDV_E000_фаза А').AsInteger() == 1:
                    activPowFaz["A"] = activPowFaz["A"] + activPow

                if el.LookupParameter('BDV_E000_фаза В').AsInteger() == 1:
                    activPowFaz["B"] = activPowFaz["B"] + activPow

                if el.LookupParameter('BDV_E000_фаза С').AsInteger() == 1:
                    activPowFaz["C"] = activPowFaz["C"] + activPow

            if el.LookupParameter('BDV_E000_380').AsInteger():
                # предупреждение, что включена фаза при 380В
                if HowManyPhases(el).getCount() > 0:
                    raise ErrorSetPhasesIn380(el)

                activPow0_33 = activPow / 3

                activPowFaz["A"] = activPowFaz["A"] + activPow0_33
                activPowFaz["B"] = activPowFaz["B"] + activPow0_33
                activPowFaz["C"] = activPowFaz["C"] + activPow0_33

        return activPowFaz

    def getTokFaz(self):
        """словарь тока,А всех элементов одной панели пофазно
        """

        tokFaz = {"A": 0.0, "B": 0.0, "C": 0.0}

        for el in self.elements:
            paramTok = el.LookupParameter('BDV_E000_Iном')
            if not paramTok:
                raise ErrorParameterTokMissing(el)

            tok = paramTok.AsInteger()

            if el.LookupParameter('BDV_E000_220').AsInteger():
                # предупреждение, что включено больше одной фазы
                if HowManyPhases(el).getCount() > 1:
                    raise ErrorMultiplePhases(el)

                if el.LookupParameter('BDV_E000_фаза А').AsInteger() == 1:
                    tokFaz["A"] = tokFaz["A"] + tok

                if el.LookupParameter('BDV_E000_фаза В').AsInteger() == 1:
                    tokFaz["B"] = tokFaz["B"] + tok

                if el.LookupParameter('BDV_E000_фаза С').AsInteger() == 1:
                    tokFaz["C"] = tokFaz["C"] + tok

            if el.LookupParameter('BDV_E000_380').AsInteger():
                # предупреждение, что включена фаза при 380В
                if HowManyPhases(el).getCount() > 0:
                    raise ErrorSetPhasesIn380(el)

                tokFaz["A"] = tokFaz["A"] + tok
                tokFaz["B"] = tokFaz["B"] + tok
                tokFaz["C"] = tokFaz["C"] + tok

        return tokFaz

    def getApparentPowerSum(self):
        """суммарная кажущаяся/полная мощность,кВА всех элементов одной панели
        """

        # apparent - кажущаяся/полная мощность
        sumApparentPow = [0.0]

        for el in self.elements:
            activePow = el.LookupParameter('BDV_E000_Активная мощность кВт').AsDouble()
            cos = el.LookupParameter('BDV_E000_cos φ').AsDouble()

            # чтоб не было деления на ноль предупреждение BDV_E000_cos φ == 0
            if cos == 0:
                raise ErrorCosIsNull(el)

            sumApparentPow[0] = sumApparentPow[0] + (activePow / cos)

        return sumApparentPow[0]

    def getActivPowerSum(self):
        """суммарная активная мощность,кВт всех одно и трехфазных элементов одной панели
        """
        # просуммировали словарь
        return sum([self.activPowFaz["A"], self.activPowFaz["B"], self.activPowFaz["C"]])

    def getCosSum(self):
        """приведенный косинус к вводу панели всех одно и трехфазных элементов этой панели
        """
        return round(self.аctivPowerSum / self.apparentPowerSum, 2)

    def getTgSum(self):
        """приведенный тангенс к вводу панели всех одно и трехфазных элементов этой панели
        """
        if self.cosSum != 0:
            return pow((1 - pow(self.cosSum, 2)), 0.5) / self.cosSum
        else:
            return self.cosSum

    def getReactivPowerSum(self):
        """суммарная реактивная мощность,квар всех одно и трехфазных элементов одной панели
        """
        return self.аctivPowerSum * self.tgSum

    def getTokFazaA(self):
        """ток фазы А, всех одно и трехфазных элементов одной панели
        """
        return self.tokFaz["A"]

    def getTokFazaB(self):
        """ток фазы B, всех одно и трехфазных элементов одной панели
        """
        return self.tokFaz["B"]

    def getTokFazaC(self):
        """ток фазы C, всех одно и трехфазных элементов одной панели
        """
        return self.tokFaz["C"]

    def getTokFromMaxFaz(self):
        """трехфазный ток по максимально загруженной фазе всех одно и трехфазных элементов одной панели
        """
        # считаем, что во всех трех фазах течет ток, как в наиболее загруженной фазе
        # потому принимаем его как ток на вводе
        # токи в каждой фазе не суммируются в отличие от мощностей
        return sorted([self.tokFaz["A"], self.tokFaz["B"], self.tokFaz["C"]])[2]

    def getAsymmetryTokFazAB(self):
        """неравномерность токов в фазах A и B, %
        """
        return round(abs((self.tokFaz["A"] / self.tokFaz["B"] - 1.0)) * 100, 1)

    def getAsymmetryTokFazBC(self):
        """неравномерность токов в фазах B и C, %
        """
        return round(abs((self.tokFaz["B"] / self.tokFaz["C"] - 1.0)) * 100, 1)

    def getAsymmetryTokFazAC(self):
        """неравномерность токов в фазах A и C, %
        """
        return round(abs((self.tokFaz["A"] / self.tokFaz["C"] - 1.0)) * 100, 1)

    def getLocationXYZ(self):
        """возвращает xyz созданное на основе точки размещения семейства с наименьшей координатой X
        """
        familyAnnotation = sorted(self.elements, key=lambda elem: elem.Location.Point.X, reverse=False)[0]
        familyXYZ = familyAnnotation.Location.Point

        return DB.XYZ(
                        familyXYZ.X,
                        familyXYZ.Y - DB.UnitUtils.ConvertToInternalUnits(
                                    self.offsetForY, DB.UnitTypeId.Millimeters),
                        familyXYZ.Z
                        )
