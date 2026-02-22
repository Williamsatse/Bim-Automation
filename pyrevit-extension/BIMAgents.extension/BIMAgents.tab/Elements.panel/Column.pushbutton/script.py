# -*- coding: utf-8 -*-
"""
BIM Agent - Creation de Colonne
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Parametres
COL_WIDTH_MM = 300
COL_DEPTH_MM = 300
COL_HEIGHT_M = 3.0

COL_WIDTH = COL_WIDTH_MM / 304.8
COL_DEPTH = COL_DEPTH_MM / 304.8
COL_HEIGHT = COL_HEIGHT_M * 3.28084


def get_active_level(doc):
    """Recupere le niveau actif"""
    active_view = doc.ActiveView
    
    if hasattr(active_view, 'GenLevel') and active_view.GenLevel:
        return active_view.GenLevel
    
    view_elevation = active_view.Origin.Z
    closest_level = None
    min_diff = float('inf')
    
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        diff = abs(lvl.Elevation - view_elevation)
        if diff < min_diff:
            min_diff = diff
            closest_level = lvl
    
    return closest_level


def create_column(doc, uidoc):
    """Cree une colonne"""
    
    level = get_active_level(doc)
    
    if not level:
        TaskDialog.Show("Erreur", "Aucun niveau detecte. Change de vue ou passe en plan.")
        return None
    
    col_type = None
    for fam in FilteredElementCollector(doc).OfClass(FamilySymbol):
        if fam.Category and fam.Category.Name in ["Structural Columns", "Colonnes structurelles"]:
            col_type = fam
            break
    
    if not col_type:
        TaskDialog.Show("Erreur", "Aucun type de colonne trouve!")
        return None
    
    if not col_type.IsActive:
        col_type.Activate()
        doc.Regenerate()
    
    TaskDialog.Show("Info", "Clique pour placer la colonne")
    point = uidoc.Selection.PickPoint("Point de placement")
    
    with Transaction(doc, "Creer Colonne") as t:
        t.Start()
        
        column = doc.Create.NewFamilyInstance(
            point, 
            col_type, 
            level, 
            StructuralType.Column
        )
        
        # Ajuste la hauteur
        top_offset = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM)
        if top_offset:
            top_offset.Set(COL_HEIGHT)
        
        t.Commit()
    
    TaskDialog.Show("Succes", 
        "Colonne creee!\n"
        "Dimensions: " + str(COL_WIDTH_MM) + "x" + str(COL_DEPTH_MM) + "mm\n"
        "Hauteur: " + str(COL_HEIGHT_M) + "m\n"
        "Niveau: " + level.Name)
    
    return column


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_column(doc, uidoc)
