"""
BIM Agent - Création de Mur
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres
WALL_THICKNESS_MM = 200
WALL_HEIGHT_M = 2.8
TARGET_LEVEL = "Niveau 1"

WALL_THICKNESS = WALL_THICKNESS_MM / 304.8
WALL_HEIGHT = WALL_HEIGHT_M * 3.28084


def create_wall(doc, uidoc):
    """Crée un mur"""
    
    base_level = None
    top_level = None
    
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            base_level = lvl
        if base_level and lvl.Elevation > base_level.Elevation:
            if not top_level or lvl.Elevation < top_level.Elevation:
                top_level = lvl
    
    if not base_level:
        TaskDialog.Show("Erreur", "Niveau '" + TARGET_LEVEL + "' non trouvé!")
        return None
    
    wall_type = None
    for wt in FilteredElementCollector(doc).OfClass(WallType):
        if wt.Kind == WallKind.Basic:
            wall_type = wt
            break
    
    if not wall_type:
        TaskDialog.Show("Erreur", "Aucun type de mur trouvé!")
        return None
    
    TaskDialog.Show("Info", "Dessinez la ligne du mur (2 points)")
    
    start_point = uidoc.Selection.PickPoint("Point de départ")
    end_point = uidoc.Selection.PickPoint("Point de fin")
    
    line = Line.CreateBound(start_point, end_point)
    
    with Transaction(doc, "Créer Mur") as t:
        t.Start()
        
        wall = Wall.Create(
            doc,
            line,
            wall_type.Id,
            base_level.Id,
            WALL_HEIGHT,
            0.0,
            False,
            False
        )
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        "Mur créé!\\n"
        "Épaisseur: " + str(WALL_THICKNESS_MM) + "mm\\n"
        "Hauteur: " + str(WALL_HEIGHT_M) + "m\\n"
        "Niveau: " + TARGET_LEVEL)
    
    return wall


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_wall(doc, uidoc)
