# -*- coding: utf-8 -*
# module rename_circuit.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List
import json

import sys
sys.path += IN[0].DirectoryName

doc = DM.Instance.CurrentDBDocument

OUT = [fix.MEPModel.GetElectricalSystems() for fix in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalFixtures) if fix.Id.IntegerValue==7118102]

