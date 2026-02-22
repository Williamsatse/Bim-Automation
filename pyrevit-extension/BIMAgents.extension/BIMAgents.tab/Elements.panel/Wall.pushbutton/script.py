# -*- coding: utf-8 -*-
"""
BIM Agent - Creation de Mur
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Parametres
WALL_THICKNESS_MM = 200
WALL_HEIGHT_M = 2.8

WALL_THICKNESS = WALL_THICKNESS_MM / 304.8
WALL_HEIGHT = WALL_HEIGHT_M * 3.28084


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


def create_wall(doc, uidoc):
    """Cree un mur"""
    
    base_level = get_active_level(doc)
    
    if not base_level:
        TaskDialog.Show("Erreur", "Aucun niveau detecte. Passe en vue de plan.")
        return None
    
    wall_type = None
    for wt in FilteredElementCollector(doc).OfClass(WallType):
        if wt.Kind == WallKind.Basic:
            wall_type = wt
            break
    
    if not wall_type:
        TaskDialog.Show("Erreur", "Aucun type de mur trouve!")
        return None
    
    TaskDialog.Show("Info", "Dessine le mur (2 points)")
    
    start_point = uidoc.Selection.PickPoint("Point de depart")
    end_point = uidoc.Selection.PickPoint("Point de fin")
    
    line = Line.CreateBound(start_point, end_point)
    
    with Transaction(doc, "Creer Mur") as t:
        t.Start()
        
        # WallType ne necessite pas d'activation
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
    
    TaskDialog.Show("Succes", 
        "Mur cree!\n"
        "Epaisseur: " + str(WALL_THICKNESS_MM) + "mm\n"
        "Hauteur: " + str(WALL_HEIGHT_M) + "m\n"
        "Niveau: " + base_level.Name)
    
    return wall


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_wall(doc, uidoc)
