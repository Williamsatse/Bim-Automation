# -*- coding: utf-8 -*-
"""
BIM Agent - Creation de Dalle
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Parametres
FLOOR_THICKNESS_MM = 200
IS_STRUCTURAL = True

FLOOR_THICKNESS = FLOOR_THICKNESS_MM / 304.8


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


def create_floor(doc, uidoc):
    """Cree une dalle"""
    
    level = get_active_level(doc)
    
    if not level:
        TaskDialog.Show("Erreur", "Aucun niveau detecte.")
        return None
    
    floor_type = None
    for ft in FilteredElementCollector(doc).OfClass(FloorType):
        floor_type = ft
        break
    
    if not floor_type:
        TaskDialog.Show("Erreur", "Aucun type de dalle trouve!")
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
    
    with Transaction(doc, "Creer Dalle") as t:
        t.Start()
        
        # FloorType ne necessite pas d'activation
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
    
    TaskDialog.Show("Succes", 
        "Dalle creee!\n"
        "Epaisseur: " + str(FLOOR_THICKNESS_MM) + "mm\n"
        "Niveau: " + level.Name + "\n"
        "Structurelle: " + ('Oui' if IS_STRUCTURAL else 'Non'))
    
    return floor


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_floor(doc, uidoc)
