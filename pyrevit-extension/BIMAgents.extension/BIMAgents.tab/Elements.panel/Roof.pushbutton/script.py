# -*- coding: utf-8 -*-
"""
BIM Agent - Creation de Toit
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Parametres
ROOF_SLOPE_DEG = 30.0


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


def create_roof(doc, uidoc):
    """Cree un toit"""
    
    level = get_active_level(doc)
    
    if not level:
        TaskDialog.Show("Erreur", "Aucun niveau detecte.")
        return None
    
    roof_type = None
    for rt in FilteredElementCollector(doc).OfClass(RoofType):
        roof_type = rt
        break
    
    if not roof_type:
        TaskDialog.Show("Erreur", "Aucun type de toit trouve!")
        return None
    
    TaskDialog.Show("Info", "Selectionne les points du contour (ESC pour finir)")
    
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
    
    curve_loop = CurveLoop()
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        line = Line.CreateBound(start, end)
        curve_loop.Append(line)
    
    with Transaction(doc, "Creer Toit") as t:
        t.Start()
        
        try:
            roof = Floor.Create(doc, [curve_loop], roof_type.Id, level.Id)
        except:
            curve_array = CurveArray()
            for curve in curve_loop:
                curve_array.Append(curve)
            roof = doc.Create.NewRoof(curve_array, roof_type, level)
        
        t.Commit()
    
    TaskDialog.Show("Succes", 
        "Toit cree!\n"
        "Pente: " + str(ROOF_SLOPE_DEG) + "deg\n"
        "Niveau: " + level.Name)
    
    return roof


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_roof(doc, uidoc)
