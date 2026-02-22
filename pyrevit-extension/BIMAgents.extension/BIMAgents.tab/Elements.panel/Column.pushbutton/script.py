"""
BIM Agent - Création de Colonne
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres
COL_WIDTH_MM = 300
COL_DEPTH_MM = 300
COL_HEIGHT_M = 3.0
TARGET_LEVEL = "Niveau 1"

COL_WIDTH = COL_WIDTH_MM / 304.8
COL_DEPTH = COL_DEPTH_MM / 304.8
COL_HEIGHT = COL_HEIGHT_M * 3.28084


def create_column(doc, uidoc):
    """Crée une colonne structurelle"""
    
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", "Niveau '" + TARGET_LEVEL + "' non trouvé!")
        return None
    
    col_type = None
    for fam in FilteredElementCollector(doc).OfClass(FamilySymbol):
        if fam.Category and fam.Category.Name in ["Structural Columns", "Colonnes structurelles"]:
            col_type = fam
            break
    
    if not col_type:
        TaskDialog.Show("Erreur", "Aucun type de colonne trouvé!")
        return None
    
    if not col_type.IsActive:
        col_type.Activate()
        doc.Regenerate()
    
    TaskDialog.Show("Info", "Cliquez pour placer la colonne")
    point = uidoc.Selection.PickPoint("Point de placement")
    
    with Transaction(doc, "Créer Colonne") as t:
        t.Start()
        
        column = doc.Create.NewFamilyInstance(
            point, 
            col_type, 
            level, 
            StructuralType.Column
        )
        
        top_offset = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM)
        if top_offset:
            top_offset.Set(COL_HEIGHT)
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        "Colonne créée!\\n"
        "Dimensions: " + str(COL_WIDTH_MM) + "x" + str(COL_DEPTH_MM) + "mm\\n"
        "Hauteur: " + str(COL_HEIGHT_M) + "m\\n"
        "Niveau: " + TARGET_LEVEL)
    
    return column


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_column(doc, uidoc)
