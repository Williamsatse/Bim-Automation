"""
BIM Agent - Création de Dalle
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres
FLOOR_THICKNESS_MM = 200
TARGET_LEVEL = "Niveau 1"
IS_STRUCTURAL = True

FLOOR_THICKNESS = FLOOR_THICKNESS_MM / 304.8


def create_floor(doc, uidoc):
    """Crée une dalle"""
    
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", "Niveau '" + TARGET_LEVEL + "' non trouvé!")
        return None
    
    floor_type = None
    for ft in FilteredElementCollector(doc).OfClass(FloorType):
        floor_type = ft
        break
    
    if not floor_type:
        TaskDialog.Show("Erreur", "Aucun type de dalle trouvé!")
        return None
    
    TaskDialog.Show("Info", "Sélectionnez les points du contour de la dalle (ESC pour terminer)")
    
    points = []
    while True:
        try:
            point = uidoc.Selection.PickPoint("Point suivant")
            projected = XYZ(point.X, point.Y, level.Elevation)
            points.append(projected)
        except:
            break
    
    if len(points) < 3:
        TaskDialog.Show("Erreur", "Il faut au moins 3 points!")
        return None
    
    curve_loop = CurveLoop()
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        line = Line.CreateBound(start, end)
        curve_loop.Append(line)
    
    with Transaction(doc, "Créer Dalle") as t:
        t.Start()
        
        try:
            floor = Floor.Create(doc, [curve_loop], floor_type.Id, level.Id)
        except:
            curve_array = CurveArray()
            for curve in curve_loop:
                curve_array.Append(curve)
            floor = doc.Create.NewFloor(curve_array, floor_type, level, False)
        
        if IS_STRUCTURAL and floor:
            param = floor.get_Parameter(BuiltInParameter.FLOOR_PARAM_IS_STRUCTURAL)
            if param:
                param.Set(True)
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        "Dalle créée!\\n"
        "Épaisseur: " + str(FLOOR_THICKNESS_MM) + "mm\\n"
        "Niveau: " + TARGET_LEVEL + "\\n"
        "Structurelle: " + ('Oui' if IS_STRUCTURAL else 'Non'))
    
    return floor


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_floor(doc, uidoc)
