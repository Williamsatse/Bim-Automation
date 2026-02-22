# -*- coding: utf-8 -*-
"""
BIM Agent - Creation de Poutre
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Parametres modifiables
BEAM_WIDTH_MM = 300
BEAM_HEIGHT_MM = 500

# Conversion mm -> pieds
BEAM_WIDTH = BEAM_WIDTH_MM / 304.8
BEAM_HEIGHT = BEAM_HEIGHT_MM / 304.8


def get_active_level(doc):
    """Recupere le niveau actif de la vue courante"""
    active_view = doc.ActiveView
    
    # Essaie de trouver le niveau associe a la vue
    if hasattr(active_view, 'GenLevel') and active_view.GenLevel:
        return active_view.GenLevel
    
    # Cherche un niveau qui correspond a l'elevation de la vue
    view_elevation = active_view.Origin.Z
    closest_level = None
    min_diff = float('inf')
    
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        diff = abs(lvl.Elevation - view_elevation)
        if diff < min_diff:
            min_diff = diff
            closest_level = lvl
    
    return closest_level


def list_available_levels(doc):
    """Liste tous les niveaux disponibles"""
    levels = []
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        levels.append(lvl.Name)
    return sorted(levels)


def create_beam(doc, uidoc):
    """Cree une poutre structurelle"""
    
    # Recupere le niveau actif
    level = get_active_level(doc)
    
    if not level:
        # Liste les niveaux disponibles
        available_levels = list_available_levels(doc)
        if not available_levels:
            TaskDialog.Show("Erreur", "Aucun niveau trouve dans le projet!")
            return None
        
        # Affiche les niveaux disponibles
        levels_text = "\n".join(["- " + l for l in available_levels[:10]])
        TaskDialog.Show("Niveaux disponibles", 
            "Niveaux dans ton projet:\n" + levels_text + 
            "\n\nModifie le nom dans le code ou change de vue.")
        return None
    
    # Trouve un type de poutre
    beam_type = None
    collector = FilteredElementCollector(doc).OfClass(FamilySymbol)
    
    for fam in collector:
        if fam.Category:
            cat_name = fam.Category.Name
            # Cherche les categories de poutres (anglais/francais)
            if cat_name in ["Structural Framing", "Charpente", "Poutres", "Framing", "Structural Framing"]:
                beam_type = fam
                break
            # Si c'est une famille utilisable comme poutre
            if "beam" in cat_name.lower() or "poutre" in cat_name.lower():
                beam_type = fam
                break
    
    # Si toujours pas trouve, prend n'importe quel FamilySymbol dispo
    if not beam_type:
        for fam in collector:
            if fam and hasattr(fam, 'IsActive'):
                beam_type = fam
                break
    
    if not beam_type:
        TaskDialog.Show("Erreur", 
            "Aucun type de poutre trouve!\n\n"
            "Pour charger une famille:\n"
            "1. Insert -> Load Family\n"
            "2. Va dans Structural Framing\n"
            "3. Charge une famille de poutres\n"
            "(ex: M_Concrete-Rectangular Beam.rfa)")
        return None
    
    # Demande les points
    TaskDialog.Show("Info", "Clique pour le point de depart de la poutre")
    start_point = uidoc.Selection.PickPoint("Point de depart")
    
    TaskDialog.Show("Info", "Clique pour le point de fin")
    end_point = uidoc.Selection.PickPoint("Point de fin")
    
    # Cree la ligne
    line = Line.CreateBound(start_point, end_point)
    
    # Cree la poutre
    with Transaction(doc, "Creer Poutre") as t:
        t.Start()
        
        # Active le type a l'interieur de la transaction
        if not beam_type.IsActive:
            beam_type.Activate()
            doc.Regenerate()
        
        beam = doc.Create.NewFamilyInstance(line, beam_type, level, StructuralType.Beam)
        
        # Ajuste la hauteur
        offset_param1 = beam.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END0_ELEVATION)
        offset_param2 = beam.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END1_ELEVATION)
        
        if offset_param1 and offset_param2:
            offset = (BEAM_HEIGHT / 2)
            offset_param1.Set(offset)
            offset_param2.Set(offset)
        
        t.Commit()
    
    TaskDialog.Show("Succes", 
        "Poutre creee!\n"
        "Dimensions: " + str(BEAM_WIDTH_MM) + "x" + str(BEAM_HEIGHT_MM) + "mm\n"
        "Niveau: " + level.Name)
    
    return beam


# Point d'entree pyRevit
if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_beam(doc, uidoc)
