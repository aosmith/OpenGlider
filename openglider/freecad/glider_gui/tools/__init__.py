import FreeCAD
import FreeCADGui as Gui

from _glider import OGGlider, OGGliderVP
from _tools import base_tool, export_2d, import_2d
from airfoil_tool import airfoil_tool
from shape_tool import shape_tool
from arc_tool import arc_tool
from aoa_tool import aoa_tool
from ballooning_tool import ballooning_tool
from line_tool import line_tool
from merge_tool import airfoil_merge_tool, ballooning_merge_tool
from openglider.plots import flatten_glider


# ICONS:
# the openglider implementation in freecad will be splitted into 3 parts. each will have a consistent icon color-sheme:
# (colors can be found in openglider/freecad/glidergui/icons/freecad-color.gpl)
# to use this with inkscape: ln -s ..../openglider/freecad/glidergui/icons/freecad-color.gpl .../.config/inkscape/palettes/

#   -import export                                          -?
#   -construction (shape, arc, lines, aoa, ...)             -blue
#   -simulation                                             -yellow
#   -optimisation                                           -red


class BaseCommand(object):
    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap': '.svg', 'MenuText': 'Text', 'ToolTip': 'Text'}
        pass

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        obj = Gui.Selection.getSelection()
        if len(obj) > 0:
            obj = obj[0]
            if check_glider(obj):
                test = Gui.Control.showDialog(self.tool(obj))

    def tool(self, obj):
        return base_tool(obj)


class Gl2d_Export(object):
    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap': 'gl2d_export.svg', 'MenuText': 'export 2D', 'ToolTip': 'export 2D'}
        pass

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        proceed = False
        obj = Gui.Selection.getSelection()
        if len(obj) > 0:
            obj = obj[0]
            if check_glider(obj):
                proceed = True
        if proceed:
            export_2d(obj)


class Gl2d_Import(object):
    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap': 'gl2d_import.svg', 'MenuText': 'import 2D', 'ToolTip': 'import 2D'}
        pass

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        proceed = False
        obj = Gui.Selection.getSelection()
        if len(obj) > 0:
            obj = obj[0]
            if check_glider(obj):
                proceed = True
        if proceed:
            import_2d(obj)


class Pattern_Tool(object):
    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap': 'pattern_tool.svg', 'MenuText': 'unwrap glider', 'ToolTip': 'unwrap glider'}
        pass

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        proceed = False
        obj = Gui.Selection.getSelection()
        if len(obj) > 0:
            obj = obj[0]
            if check_glider(obj):
                proceed = True
        if proceed:
            pattern_doc = FreeCAD.newDocument()
            from Draft import makeWire
            flat_glider = flatten_glider(obj.glider_instance)
            max_last = [0, 0]
            draw_area = flat_glider.values()[0]
            for da in flat_glider.values()[1:]:
                draw_area.join(da)
            for i, part in enumerate(draw_area.parts):
                grp = pattern_doc.addObject("App::DocumentObjectGroup","Panel_" + str(i))
                layer_dict = part.layer_dict
                for layer in layer_dict:
                    for j, line in enumerate(layer_dict[layer]):
                        a = makeWire(map(Pattern_Tool.fcvec, line), face=False)
                        grp.addObject(a)


    @staticmethod
    def fcvec(vec):
        return FreeCAD.Vector(vec[0], vec[1], 0.)


class CreateGlider(BaseCommand):
    def GetResources(self):
        return {'Pixmap': "new_glider.svg", 'MenuText': 'glider', 'ToolTip': 'glider'}

    def Activated(self):
        a = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Glider")
        OGGlider(a)
        OGGliderVP(a.ViewObject)
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")


class Shape_Tool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'shape_tool.svg', 'MenuText': 'shape', 'ToolTip': 'shape'}

    def tool(self, obj):
        return shape_tool(obj)


class Arc_Tool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'arc_tool.svg', 'MenuText': 'arc', 'ToolTip': 'arc'}

    def tool(self, obj):
        return arc_tool(obj)


class Aoa_Tool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'aoa_tool.svg', 'MenuText': 'aoa', 'ToolTip': 'aoa'}

    def tool(self, obj):
        return aoa_tool(obj)


class Airfoil_Tool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'airfoil_tool.svg', 'MenuText': 'airfoil', 'ToolTip': 'airfoil'}

    def tool(self, obj):
        return airfoil_tool(obj)


class AirfoilMergeTool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'airfoil_merge_tool.svg', 'MenuText': 'airfoil merge', 'ToolTip': 'airfoil merge'}

    def tool(self, obj):
        return airfoil_merge_tool(obj)


class Ballooning_Tool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'ballooning_tool.svg', 'MenuText': 'ballooning', 'ToolTip': 'ballooning'}

    def tool(self, obj):
        return ballooning_tool(obj)


class BallooningMergeTool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'ballooning_merge_tool.svg', 'MenuText': 'ballooning merge', 'ToolTip': 'ballooning merge'}

    def tool(self, obj):
        return ballooning_merge_tool(obj)


class Line_Tool(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'line_tool.svg', 'MenuText': 'lines', 'ToolTip': 'lines'}

    def tool(self, obj):
        return line_tool(obj)


def check_glider(obj):
    if "glider_instance" in obj.PropertiesList and "glider_2d" in obj.PropertiesList:
        return True
    else:
        return False
