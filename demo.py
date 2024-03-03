# -*- coding: utf-8 -*
# module create_circuit_stoyak_shield.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM

import sys
sys.path += [IN[0].DirectoryName]

from create_circuit_stoyak_floor_shield.select_connectors import SelectConnectors
from create_circuit_stoyak_floor_shield.path_for_circuit import PathForCircuit
from create_circuit_stoyak_floor_shield.user_form_create_circuit_stoyak_floor_shield import UserFormCreateCircuitStoyak
from create_circuit_stoyak_floor_shield.user_warning_create_circuit_stoyak_floor_shield import ErrorActiveView,\
                                                                                    ErrorCancelButton

doc = DM.Instance.CurrentDBDocument
uiapp = DM.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument

# ФОРМА ПОЛЬЗОВАТЕЛЯ
userForm = UserFormCreateCircuitStoyak()
userForm.ShowDialog()
if not isinstance(doc.ActiveView, DB.ViewSection):
    raise ErrorActiveView()
if userForm.dictUserSelect["cancelScript"]:
    raise ErrorCancelButton()

unitLengType = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
unitAreaType = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Area).GetUnitTypeId()


with DB.Transaction(doc, 'CreateCircuitStoyakShield') as t:
    t.Start()
    # ЩИТЫ
    elementIdFamily = [family.Id for family in FEC(doc).OfClass(DB.Family)
                                    if "Щит этажный" in family.Name or "офисов" in family.Name]

    # ВЫБОР ПАНЕЛИ УКАЗАННОЙ ПОЛЬЗОВАТЕЛЕМ
    panelСonnection = 0
    for element in FEC(doc).OfCategory(
                DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
        if element.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString():
            panelName = element.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
            if userForm.dictUserSelect["objectInVRY"] == panelName[:panelName.rfind('.')]:
                panelСonnection = element
    conPanel = [conp for conp in panelСonnection.MEPModel.ConnectorManager.Connectors 
            if conp.Domain == DB.Domain.DomainElectrical][0]

    selectCon = SelectConnectors(doc, elementIdFamily, panelСonnection)
    shieldSortLevel = selectCon.get_shieldSortLevel()
    endConnectors = selectCon.get_endConnectors()

    # ПОСТРОЕНИЕ ЦЕПЕЙ ОТ ЩЭ К ЩЭ
    doc.Settings.ElectricalSetting.CircuitPathOffset = DB.UnitUtils.ConvertToInternalUnits(
                        0, #  укажи смещение в миллиметрах
                        unitLengType
                        )
    OUT = []
    for name_group, sort_list_shield in shieldSortLevel.items():
        if len(sort_list_shield) > 1:
            for i in range(len(sort_list_shield) - 1):
                list_con = [c for c in sort_list_shield[i].MEPModel.ConnectorManager.Connectors 
                        if c.Domain == DB.Domain.DomainElectrical]
                for currentCon in list_con:
                    if [conctr for conctr in currentCon.AllRefs]:
                        continue
                    circuit = DB.Electrical.ElectricalSystem.Create(currentCon, currentCon.ElectricalSystemType)
                    circuit.SelectPanel(sort_list_shield[i+1])
                    OUT.append(circuit.Id)

    dictPath = {}
    # ПОСТРОЕНИЕ ЦЕПЕЙ ПОДКЛЮЧЕНИЯ К ВРУ (К ПАНЕЛИ УКАЗАНОЙ ПОЛЬЗОВАТЕЛЕМ)
    dtValidPath = {}
    for name_group, sort_list_shield in shieldSortLevel.items():
        dictPath[name_group] = []
        dtValidPath[name_group] = []
        list_con = [connector for connector in sort_list_shield[-1].MEPModel.ConnectorManager.Connectors 
                if connector.Domain == DB.Domain.DomainElectrical]
        for currentCon in list_con:
            pathForCon = PathForCircuit(
                sort_list_shield[-1], currentCon, conPanel, endConnectors[name_group][0])
            dictPath[name_group].append(pathForCon.get_path())
            if [conctr for conctr in currentCon.AllRefs]:
                continue
            circuit = DB.Electrical.ElectricalSystem.Create(currentCon, currentCon.ElectricalSystemType)
            circuit.SelectPanel(panelСonnection)
            doc.Regenerate()
            dtValidPath[name_group].append(circuit.IsCircuitPathValid(pathForCon.get_path()))
            circuit.SetCircuitPath(pathForCon.get_path())

            OUT.append(circuit.Id)
    t.Commit()
