# -*- coding: utf-8 -*-
"""
BIM Agent - Création de Toit
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr
import math

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres
ROOF_SLOPE_DEG = 30.0
TARGET_LEVEL = "Niveau 2"


def create_roof(doc, uidoc):
    """Crée un toit"""
    
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", "Niveau '" + TARGET_LEVEL + "' non trouvé!")
        return None
    
    roof_type = None
    for rt in FilteredElementCollector(doc).OfClass(RoofType):
        roof_type = rt
        break
    
    if not roof_type:
        TaskDialog.Show("Erreur", "Aucun type de toit trouvé!")
        return None
    
    TaskDialog.Show("Info", "Sélectionnez les points du contour du toit (ESC pour terminer)")
    
    points = []
    while True:
        try:
            point = uidoc.Selection.PickPoint("Point suivant")
            points.append(point)
        except:
            break
    
    if len(points) < 3:
        TaskDialog.Show("Erreur", "Il faut au moins 3 points!")
        return None
    
    # Crée le contour
    curve_loop = CurveLoop()
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        line = Line.CreateBound(start, end)
        curve_loop.Append(line)
    
    with Transaction(doc, "Créer Toit") as t:
        t.Start()
        
        try:
            roof = Floor.Create(
                doc,
                [curve_loop],
                roof_type.Id,
                level.Id
            )
        except:
            # Fallback pour anciennes versions
            curve_array = CurveArray()
            for curve in curve_loop:
                curve_array.Append(curve)
            roof = doc.Create.NewRoof(curve_array, roof_type, level)
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        "Toit créé!\\n"
        "Pente: " + str(ROOF_SLOPE_DEG) + "°\\n"
        "Niveau: " + TARGET_LEVEL)
    
    return roof


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_roof(doc, uidoc)
