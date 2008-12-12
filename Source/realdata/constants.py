"""

constants.py

this file contains any application-wide constants:
help, about messages, version numbers, geometry, styles, etc

djo, 5/07

"""

# ------------------------- imports -------------------------
import sys



# ------------------------- version -------------------------
version = "0.87"


# ------------------------- messages -------------------------
# ......................... about .........................
aboutmessage = """

Neuroptikon demo v%s

by Donald J. Olbris

"""

# ......................... help .........................
helpmessage = """

Neuroptikon



Neuroptikon is a demonstration/prototype of a tool for visualizing
neural circuits in the fly brain central complex.

The squares represent brain regions; the lines represent neurons.

Basic operation:
-- to select a region or connection, click on it
-- to add to a selection, shift-click
-- to deselect, click on the background

Highlighting: in addition to the click-selection, you may also highlight
subsets of connections in different colors depending on some simple 
criteria.  Using the View menu, you may choose to highlight neurons by
where they have input or output, or highlight any object by the text 
contained in their names or descriptions (use View-->Show Info Window
to display all that information).

Highlighting notes:
-- highlights "stack", but only the most recent is visible
-- Highlight by text... is case-insensitive
-- Highlight by text...: if you enter multiple words, target must have
    all of them to be highlighted
-- highlights accumulate; if you use the same color, new results are added to
    previous results
-- you may hide, show, or clear highlighting from the View menu


Legend:
PB = protocerebral bridge (arbitrary numbering)
FB = fan-shaped body (arbitrary labeling)
EB = elliptical body
VBO = ventral bodies
LTR = lateral triangles
OF = optical foci
DLPC = dorso-lateral protocerebrum (possibly ought to be medio-ventral instead??)

Neuron endings: 
-- an arrow pointing away from a region = input in region 
-- an arrow pointing toward a region = output in region
-- a square = both input and output

Source: a subset of neurons listed in Hanesch et al, Cell Tissue Res 257, 
p343 (1989)


Report problems, suggestions, etc., to Don Olbris.


"""

# ......................... info window .........................
# this template needs to be filled in with the object's name,
#   label, and comments field
infomessage = """

Name: %s

Label: %s

Comments:

%s

"""


# ------------------------- geometry etc. -------------------------
# canvas size
canvasnx = 1200
canvasny = 800


# how close you need to be to count as clicking on an object:
clicktolerance = 3



# node routing info
# displacement of routing nodes away from region edge (pix):
nodedisplacement = 20


# ------------------------- global flags -------------------------
# debug mode or not?
debug = 1


# when you click on a region, does the region highlight,
#   or do all its connections too?
selectconnectionswithregions = True

# ...and vice versa: select a connection, also select all
#   regions it has input/output in?
selectregionswithconnections = True


# draw little shapes on connection nodes:
drawnodeshapes = True


# ------------------------- styles -------------------------
# basic styling
background = "white"

# region group text: always black or matching fill color?
#   (yes, this is a bad way to do it...ought to have a separate 
#   region group style if I want to vary the text color...)
regiongrouptextblack = True
if sys.platform.startswith("win"): 
    regiongrouplabeloffset = 6
elif sys.platform.startswith("linux"):
    regiongrouplabeloffset = 6
else:
    # Mac & unknown systems
    regiongrouplabeloffset = 3

# regions have line color, line width, fill color
regionwidth = 3
regiongroupwidth = 3
regionstyles = {
    "default": ("steelblue4", regionwidth, "white"),
    "default-group": ("steelblue4", regiongroupwidth, ""),
    "default-group-fill": ("", regiongroupwidth, "lightsteelblue1"),
    "black": ("black", regionwidth, "white"),
    "brown": ("#62851a3c4", regionwidth, "white"),
    "brown-group-fill": ("", regionwidth, "burlywood2"),
    "green": ("springgreen4", regionwidth, "white"),
    "green-group-fill": ("", regionwidth, "palegreen2"),
    "invisible": ("", 1, ""),
    "orange": ("darkorange", regionwidth, "white"),
    "rose": ("palevioletred4", regionwidth, "white"),
    "rose-group": ("palevioletred2", regiongroupwidth, ""),
    "rose-group-fill": ("", regiongroupwidth, "#eecb26c5d"),
    "test": ("steelblue3", regionwidth, "gray80"),
    "purple": ("mediumpurple4", regionwidth, "white"),
    }

# connections have line color, line width, linecolor2, linecolor3; linecolor2, 3
#   are used for input, output line segments (if "", use primary color)
connectionstyles = {
    # "default": ("gray35", 2, "", ""), 
    "default": ("gray65", 1, "", ""), 
    # "test": ("gray15", 3, "green", "red"),
    "test": ("gray25", 3, "gray40", "black"),
    "alt": ("maroon", 3, "", ""), 
    }

# nodes have a shape at input and output
# possibilities:
#   ('null', ) (do nothing, for routing)
#   ('circle', radius) (looks like a square when small)
#   ('square', half sidelength)
#   ('x', half sidelength)
#   ('diamond', sidelength)
#   ('open-diamond', sidelength)
#   ('diamond-star', sidelength) (looks blobby)
#   ('open-diamond-x', sidelength) (x and open-diamond superimposed) (looks confused)
#   arrows? 'x' and 'open-diamond' look like arrow when half-covered
nodecolor = "gray20"
nodelinewidth = 2
nodestyles = {
    "i": ("open-diamond", 5),
    "o": ("x", 5),
    "b": ("square", 4),
    "r": ("null", ),
    }

# highlight styles have (at a minimum) colors...not sure what else yet,
#   but leave room
# possible: ("shadow", "color", shadow offset)
#           ("outline", "color", extrawidth)
highlightlinewidth = 4
highlightstyles = {
    # highlight styles
    "blue": ("outline", "turquoise3", highlightlinewidth),
    "gray": ("outline", "gray50", highlightlinewidth),
    "green": ("outline", "springgreen2", highlightlinewidth),
    "orange": ("outline", "orangered1", highlightlinewidth),
    "purple": ("outline", "orchid4", highlightlinewidth),
    "red": ("outline", "indianred2", highlightlinewidth),
    "yellow": ("outline", "yellow1", highlightlinewidth),
    }
# assign selection styles from existing highlight styles:
selectionstyle = "yellow"
for item in ["selection", "selection-region", "selection-connection"]:
    highlightstyles[item] = highlightstyles[selectionstyle]
# styles to use for highlighting; don't re-use selection style in this list!
activehighlightstyles = ['blue', 'gray', 'green', 'orange', 'purple', 'red']


# ------------------------- fonts -------------------------
# fonts; Tk font spec = ('Times', 12, 'italic') or 
#   ("Helvetica", 18) (for roman face)

# same sizes don't look good on every platform; win: text 
#   is too big!  win/lin: text is too thin at smaller size

if sys.platform.startswith("win"): 
    namefont = ("Helvetica", 24, "bold")
    labelfont = ("Helvetica", 18)
    regionfont = ("Helvetica", 14)
    regiongroupfont = ("Helvetica", 12, "bold")
elif sys.platform.startswith("linux"):
    namefont = ("Helvetica", 24, "bold")
    labelfont = ("Helvetica", 18)
    regionfont = ("Helvetica", 18)
    regiongroupfont = ("Helvetica", 16, "bold")
else:
    # Mac & unknown systems
    namefont = ("Helvetica", 32)
    labelfont = ("Helvetica", 18)
    regionfont = ("Helvetica", 18)
    regiongroupfont = ("Helvetica", 16)


