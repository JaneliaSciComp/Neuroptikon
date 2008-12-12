"""

realdata.py


this file contains the data to be displayed; it's stored as Python code

- this version: try to use real data


djo, 6/07

"""

# ------------------------- notes -------------------------
# be very careful with duplicate names in this file; since this
#   is Python code, any duplicate dictionary keys will silently
#   override preceding ones!  can't be checked without difficult
#   parsing!

# ------------------------- imports -------------------------
from math import pi

#import constants as const

# simple "structure" class
class struct: pass


# ------------------------- regions -------------------------
# "name": (label, geometry, "stylename", "comments/source/cite" )
# geometry is:
#   ('box', (x, y, w, h)) = x, y center, width, height
#   ('octant', (x, y, r, dr, dir)) = x, y center of whole; r distance off
#       octant from that center; dr = radial "thickness"; dir is which
#       octant: (are we point-up or flat-up??) (region only)
#   ('circle', (x, y, r)) = x, y center, r radius (regiongroup only)

# bilateral center
xc = 0  #const.canvasnx / 2.

# how tight the region group is around the regions
groupbuffer = 20

# pb = protocerebral bridge
pb = struct()
pb.y = 65
pb.width = 60
pb.height = 40
pb.dx = pb.width + 5
pb.style = "default"

# fb = fan-shaped body
fb = struct()
fb.y = 210
fb.width = 80
fb.height = 40
fb.dx = fb.width + 5
fb.style = "rose"

# eb = elliptical bodies: (anterior/posterior) x (inner/outer) x (8 columns) 
eb = struct()
eb.width = 200
eb.height = 80
eb.top = 340
eb.spacing = 130
eb.antouty = eb.top
eb.antiny = eb.top + eb.height + 5
eb.postiny = eb.top + eb.spacing + eb.height
eb.postouty = eb.top + eb.spacing + 2 * eb.height + 5
eb.dx = eb.width
eb.style = "green"

# nn = noduli
nn = struct()
nn.y = 750
nn.xoffset = 80
nn.width = 100
nn.height = 50
nn.dx = nn.width
nn.style = "brown"

# dlpc = dorso-lateral protocerebrum
dlpc = struct()
dlpc.y = 100
dlpc.xoffset = 560
dlpc.width = 60
dlpc.height = 100
dlpc.style = "purple"

# of = optic foci
of = struct()
of.y = 275
of.xoffset = 540
of.width = 80
of.height = 100
of.style = "purple"

# ltr = lateral triangles
ltr = struct()
ltr.y = 450
ltr.xoffset = 540
ltr.width = 80
ltr.height = 100
ltr.style = "purple"

# vbo = ventral bodies
vbo = struct()
vbo.y = 625
vbo.xoffset = 500
vbo.width = 120
vbo.height = 120
vbo.style = "purple"

regions = {
    # test invisible
    # "test-invisible": ("invis", ('box-invisible', (200, 270, pb.width, pb.height)), "default", ""),
    # "test-visible": ("invis", ('box', (200, 320, pb.width, pb.height)), "default", ""),
    # PB right:
    "PB-R1": ("1", ('box', (xc - 0.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, "search for me!"),
    "PB-R2": ("2", ('box', (xc - 1.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-R3": ("3", ('box', (xc - 2.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-R4": ("4", ('box', (xc - 3.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-R5": ("5", ('box', (xc - 4.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-R6": ("6", ('box', (xc - 5.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-R7": ("7", ('box', (xc - 6.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-R8": ("8", ('box', (xc - 7.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    # PB left
    "PB-L1": ("1", ('box', (xc + 0.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, "search for me!"),
    "PB-L2": ("2", ('box', (xc + 1.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-L3": ("3", ('box', (xc + 2.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-L4": ("4", ('box', (xc + 3.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-L5": ("5", ('box', (xc + 4.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-L6": ("6", ('box', (xc + 5.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-L7": ("7", ('box', (xc + 6.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    "PB-L8": ("8", ('box', (xc + 7.5 * pb.dx, pb.y, pb.width, pb.height)), pb.style, ""),
    # FB
    "FB-A": ("A", ('box', (xc - 3.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    "FB-B": ("B", ('box', (xc - 2.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    "FB-C": ("C", ('box', (xc - 1.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    "FB-D": ("D", ('box', (xc - 0.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    "FB-E": ("E", ('box', (xc + 0.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    "FB-F": ("F", ('box', (xc + 1.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    "FB-G": ("G", ('box', (xc + 2.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    "FB-H": ("H", ('box', (xc + 3.5 * fb.dx, fb.y, fb.width, fb.height)), fb.style, ""),
    # EB anterior
    "EB-ant-out": ("outer ring", ('box', (xc, eb.antouty, eb.width, eb.height)), eb.style, ""),
    "EB-ant-in": ("inner ring", ('box', (xc, eb.antiny, eb.width, eb.height)), eb.style, ""),
    # EB posterior 
    "EB-post-in": ("inner ring", ('box', (xc, eb.postiny, eb.width, eb.height)), eb.style, ""),
    "EB-post-out": ("outer ring", ('box', (xc, eb.postouty, eb.width, eb.height)), eb.style, ""),
    # noduli
    "N-L1": ("1", ('box', (xc + nn.xoffset, nn.y, nn.width, nn.height)), nn.style, ""),
    "N-L2": ("2", ('box', (xc + nn.xoffset + nn.width + 5, nn.y, nn.width, nn.height)), nn.style, ""),
    "N-R1": ("1", ('box', (xc - nn.xoffset, nn.y, nn.width, nn.height)), nn.style, ""),
    "N-R2": ("2", ('box', (xc - nn.xoffset - nn.width - 5, nn.y, nn.width, nn.height)), nn.style, ""),
    # other
    "DLPC-L": ("DLPC", ('box', (xc + dlpc.xoffset, dlpc.y, dlpc.width, dlpc.height)), dlpc.style, ""),
    "DLPC-R": ("DLPC", ('box', (xc - dlpc.xoffset, dlpc.y, dlpc.width, dlpc.height)), dlpc.style, ""),
    "OF-L": ("OF", ('box', (xc + of.xoffset, of.y, of.width, of.height)), of.style, ""),
    "OF-R": ("OF", ('box', (xc - of.xoffset, of.y, of.width, of.height)), of.style, ""),
    "LTR-L": ("LTR", ('box', (xc + ltr.xoffset, ltr.y, ltr.width, ltr.height)), ltr.style, ""),
    "LTR-R": ("LTR", ('box', (xc - ltr.xoffset, ltr.y, ltr.width, ltr.height)), ltr.style, ""),
    "VBO-L": ("VBO", ('box', (xc + vbo.xoffset, vbo.y, vbo.width, vbo.height)), vbo.style, "search for me!"),
    "VBO-R": ("VBO", ('box', (xc - vbo.xoffset, vbo.y, vbo.width, vbo.height)), vbo.style, ""),
    }


# ------------------------- connections -------------------------
# "name": (label, [nodelist], "stylename", "comments/source/cite")
# node: ("i/o", "region") or ("r", (x, y))
# should be listed from top to bottom, even if "o" is before "i"!

# if I were willing to break up the groups and ordering, I could
#   neaten up some of the connections (prevent some crossings, etc)
#   (not worth doing too early, though!)

connections = {
    # testing neurons:
    # test (has a routing node, unlike others so far)
    # "test1": ("t1", [('i', "PB-R5", 's'), ('r', 150, 200), ('o', "VBO-R", 'n')], "alt", ""),
    # test route through invisible
    # "test2": ("t2", [('i', "PB-R8", 's'), ('i', "test-invisible", 'n'), ('i', "test-invisible", 's'), ('o', "EB-ant-I3", 'n')], "alt", ""),
    # "test3": ("t3", [('i', "PB-R5", 's'), ('i', "test-invisible", 'n'), ('i', "test-invisible", 's'), ('o', "EB-ant-I4", 'n')], "alt", ""),
    # test something with a 'b' node:
    # "test4": ("t4", [('i', "PB-R8", 'w'), ('b', "OF-R", 'n')], "alt", ""),
    # "test5": ("t5", ('i', "FB-A", 'w'), ('b', "OF-R", 'e')], "alt", ""),
    # ----------------------------------------------------------------------
    # real data; sources:
    #   H = Henesch et al, Cell Tissue Res 257, p343 (1989)
    #   M = Muller et al, Cell Tissue Res 288, p159 (1997)
    #   nothing = directly from Vivek
    # VFS (H)
    "VFS-A1": ("VFS", [("i", "PB-R8", 's'), ("o", "FB-A", 'n'), ("o", "FB-A", 's'), ("b", "N-L1", 'n')], "default", "search for me!"),
    "VFS-A2": ("VFS", [("i", "PB-R7", 's'), ("o", "FB-A", 'n'), ("o", "FB-A", 's'), ("b", "N-L1", 'n')], "default", ""),
    "VFS-B1": ("VFS", [("i", "PB-R6", 's'), ("o", "FB-B", 'n'), ("o", "FB-B", 's'), ("b", "N-L1", 'n')], "default", ""),
    "VFS-B2": ("VFS", [("i", "PB-R5", 's'), ("o", "FB-B", 'n'), ("o", "FB-B", 's'), ("b", "N-L1", 'n')], "default", ""),
    "VFS-C1": ("VFS", [("i", "PB-R4", 's'), ("o", "FB-C", 'n'), ("o", "FB-C", 's'), ("b", "N-L1", 'n')], "default", ""),
    "VFS-C2": ("VFS", [("i", "PB-R3", 's'), ("o", "FB-C", 'n'), ("o", "FB-C", 's'), ("b", "N-L1", 'n')], "default", ""),
    "VFS-D1": ("VFS", [("i", "PB-R2", 's'), ("o", "FB-D", 'n'), ("o", "FB-D", 's'), ("b", "N-L1", 'n')], "default", ""),
    "VFS-D2": ("VFS", [("i", "PB-R1", 's'), ("o", "FB-D", 'n'), ("o", "FB-D", 's'), ("b", "N-L1", 'n')], "default", ""),
    "VFS-E1": ("VFS", [("i", "PB-L1", 's'), ("o", "FB-E", 'n'), ("o", "FB-E", 's'), ("b", "N-R1", 'n')], "default", ""),
    "VFS-E2": ("VFS", [("i", "PB-L2", 's'), ("o", "FB-E", 'n'), ("o", "FB-E", 's'), ("b", "N-R1", 'n')], "default", ""),
    "VFS-F1": ("VFS", [("i", "PB-L3", 's'), ("o", "FB-F", 'n'), ("o", "FB-F", 's'), ("b", "N-R1", 'n')], "default", ""),
    "VFS-F2": ("VFS", [("i", "PB-L4", 's'), ("o", "FB-F", 'n'), ("o", "FB-F", 's'), ("b", "N-R1", 'n')], "default", ""),
    "VFS-G1": ("VFS", [("i", "PB-L5", 's'), ("o", "FB-G", 'n'), ("o", "FB-G", 's'), ("b", "N-R1", 'n')], "default", ""),
    "VFS-G2": ("VFS", [("i", "PB-L6", 's'), ("o", "FB-G", 'n'), ("o", "FB-G", 's'), ("b", "N-R1", 'n')], "default", ""),
    "VFS-H1": ("VFS", [("i", "PB-L7", 's'), ("o", "FB-H", 'n'), ("o", "FB-H", 's'), ("b", "N-R1", 'n')], "default", ""),
    "VFS-H2": ("VFS", [("i", "PB-L8", 's'), ("o", "FB-H", 'n'), ("o", "FB-H", 's'), ("b", "N-R1", 'n')], "default", ""),
    # HFS (H)
    "HFS-A1": ("HFS", [("i", "PB-R8", 's'), ("b", "FB-A", 'n'), ("b", "FB-A", 's'), ("o", "VBO-R", 'n')], "default", "search for me!"),
    "HFS-A2": ("HFS", [("i", "PB-R7", 's'), ("b", "FB-A", 'n'), ("b", "FB-A", 's'), ("o", "VBO-L", 'n')], "default", ""),
    "HFS-B1": ("HFS", [("i", "PB-R6", 's'), ("b", "FB-B", 'n'), ("b", "FB-B", 's'), ("o", "VBO-R", 'n')], "default", ""),
    "HFS-B2": ("HFS", [("i", "PB-L1", 's'), ("b", "FB-B", 'n'), ("b", "FB-B", 's'), ("o", "VBO-L", 'n')], "default", ""),
    "HFS-C1": ("HFS", [("i", "PB-R5", 's'), ("b", "FB-C", 'n'), ("b", "FB-C", 's'), ("o", "VBO-L", 'n')], "default", ""),
    "HFS-C2": ("HFS", [("i", "PB-L2", 's'), ("b", "FB-C", 'n'), ("b", "FB-C", 's'), ("o", "VBO-R", 'n')], "default", ""),
    "HFS-D1": ("HFS", [("i", "PB-R4", 's'), ("b", "FB-D", 'n'), ("b", "FB-D", 's'), ("o", "VBO-L", 'n')], "default", ""),
    "HFS-D2": ("HFS", [("i", "PB-L3", 's'), ("b", "FB-D", 'n'), ("b", "FB-D", 's'), ("o", "VBO-R", 'n')], "default", ""),
    "HFS-E1": ("HFS", [("i", "PB-R3", 's'), ("b", "FB-E", 'n'), ("b", "FB-E", 's'), ("o", "VBO-L", 'n')], "default", ""),
    "HFS-E2": ("HFS", [("i", "PB-L4", 's'), ("b", "FB-E", 'n'), ("b", "FB-E", 's'), ("o", "VBO-R", 'n')], "default", ""),
    "HFS-F1": ("HFS", [("i", "PB-R2", 's'), ("b", "FB-F", 'n'), ("b", "FB-F", 's'), ("o", "VBO-L", 'n')], "default", ""),
    "HFS-F2": ("HFS", [("i", "PB-L5", 's'), ("b", "FB-F", 'n'), ("b", "FB-F", 's'), ("o", "VBO-R", 'n')], "default", ""),
    "HFS-G1": ("HFS", [("i", "PB-R1", 's'), ("b", "FB-G", 'n'), ("b", "FB-G", 's'), ("o", "VBO-L", 'n')], "default", ""),
    "HFS-G2": ("HFS", [("i", "PB-L6", 's'), ("b", "FB-G", 'n'), ("b", "FB-G", 's'), ("o", "VBO-R", 'n')], "default", ""),
    "HFS-H1": ("HFS", [("i", "PB-L7", 's'), ("b", "FB-H", 'n'), ("b", "FB-H", 's'), ("o", "VBO-R", 'n')], "default", ""),
    "HFS-H2": ("HFS", [("i", "PB-L8", 's'), ("b", "FB-H", 'n'), ("b", "FB-H", 's'), ("o", "VBO-L", 'n')], "default", ""),
    # pontine (H)
    "pontine-ae-1": ("pontine", [("i", "FB-A", 'n'), ("o", "FB-E", 'n')], "default", ""),  
    "pontine-bf-1": ("pontine", [("i", "FB-B", 'n'), ("o", "FB-F", 'n')], "default", ""),  
    "pontine-cg-1": ("pontine", [("i", "FB-C", 'n'), ("o", "FB-G", 'n')], "default", ""),  
    "pontine-dh-1": ("pontine", [("i", "FB-D", 'n'), ("o", "FB-H", 'n')], "default", ""),  
    "pontine-ae-2": ("pontine", [("o", "FB-A", 's'), ("i", "FB-E", 's')], "default", ""),  
    "pontine-bf-2": ("pontine", [("o", "FB-B", 's'), ("i", "FB-F", 's')], "default", ""),  
    "pontine-cg-2": ("pontine", [("o", "FB-C", 's'), ("i", "FB-G", 's')], "default", ""),  
    "pontine-dh-2": ("pontine", [("o", "FB-D", 's'), ("i", "FB-H", 's')], "default", ""),  
    # large field ltr-eb ring neurons (R1-3, in part)
    "ltr-eb-R1-1": ("ltr-eb", [('i', "LTR-L", 'w'), ('o', "EB-post-in", 'e')], "default", "large field ring"),
    "ltr-eb-R1-2": ("ltr-eb", [('i', "LTR-R", 'e'), ('o', "EB-post-in", 'w')], "default", "large field ring"),
    "ltr-eb-R2-1": ("ltr-eb", [('i', "LTR-L", 'w'), ('o', "EB-ant-out", 'e')], "default", "large field ring"),
    "ltr-eb-R2-2": ("ltr-eb", [('i', "LTR-R", 'e'), ('o', "EB-ant-out", 'w')], "default", "large field ring"),
    "ltr-eb-R3-1": ("ltr-eb", [('i', "LTR-L", 'w'), ('o', "EB-ant-in", 'e')], "default", "large field ring"),
    "ltr-eb-R3-2": ("ltr-eb", [('i', "LTR-R", 'e'), ('o', "EB-ant-in", 'w')], "default", "large field ring"),
    # eb-pb-vbo 
    # eb-pb-contra-vbo (evens, ant, out)
    "eb-pb-vbo-aR8": ("eb-pb-vbo", [('o', "PB-R8", 's'), ('i', "EB-ant-out", 'w'), ('i', "EB-ant-out", 'w'), ('o', "VBO-L", 'w')], "default", ""),
    # "eb-pb-vbo-aR6": ("eb-pb-vbo", [('o', "PB-R6", 's'), ('i', "EB-ant-out", 'w'), ('i', "EB-ant-out", 'w'), ('o', "VBO-L", 'w')], "default", ""),
    "eb-pb-vbo-aR4": ("eb-pb-vbo", [('o', "PB-R4", 's'), ('i', "EB-ant-out", 'w'), ('i', "EB-ant-out", 'w'), ('o', "VBO-L", 'w')], "default", ""),
    # "eb-pb-vbo-aR2": ("eb-pb-vbo", [('o', "PB-R2", 's'), ('i', "EB-ant-out", 'w'), ('i', "EB-ant-out", 'w'), ('o', "VBO-L", 'w')], "default", ""),
    "eb-pb-vbo-aL8": ("eb-pb-vbo", [('o', "PB-L8", 's'), ('i', "EB-ant-out", 'e'), ('i', "EB-ant-out", 'e'), ('o', "VBO-R", 'e')], "default", ""),
    # "eb-pb-vbo-aL6": ("eb-pb-vbo", [('o', "PB-L6", 's'), ('i', "EB-ant-out", 'e'), ('i', "EB-ant-out", 'e'), ('o', "VBO-R", 'e')], "default", ""),
    "eb-pb-vbo-aL4": ("eb-pb-vbo", [('o', "PB-L4", 's'), ('i', "EB-ant-out", 'e'), ('i', "EB-ant-out", 'e'), ('o', "VBO-R", 'e')], "default", ""),
    # "eb-pb-vbo-aL2": ("eb-pb-vbo", [('o', "PB-L2", 's'), ('i', "EB-ant-out", 'e'), ('i', "EB-ant-out", 'e'), ('o', "VBO-R", 'e')], "default", ""),
    # eb-pb-ipse-vbo (odds, post, out)
    "eb-pb-vbo-aR7": ("eb-pb-vbo", [('o', "PB-R7", 's'), ('i', "EB-post-out", 'w'), ('i', "EB-post-out", 'w'), ('o', "VBO-R", 'e')], "default", ""),
    # "eb-pb-vbo-aR5": ("eb-pb-vbo", [('o', "PB-R5", 's'), ('i', "EB-post-out", 'w'), ('i', "EB-post-out", 'w'), ('o', "VBO-R", 'e')], "default", ""),
    "eb-pb-vbo-aR3": ("eb-pb-vbo", [('o', "PB-R3", 's'), ('i', "EB-post-out", 'w'), ('i', "EB-post-out", 'w'), ('o', "VBO-R", 'e')], "default", ""),
    # "eb-pb-vbo-aR1": ("eb-pb-vbo", [('o', "PB-R1", 's'), ('i', "EB-post-out", 'w'), ('i', "EB-post-out", 'w'), ('o', "VBO-R", 'e')], "default", ""),
    "eb-pb-vbo-aL7": ("eb-pb-vbo", [('o', "PB-L7", 's'), ('i', "EB-post-out", 'e'), ('i', "EB-post-out", 'e'), ('o', "VBO-L", 'w')], "default", ""),
    # "eb-pb-vbo-aL5": ("eb-pb-vbo", [('o', "PB-L5", 's'), ('i', "EB-post-out", 'e'), ('i', "EB-post-out", 'e'), ('o', "VBO-L", 'w')], "default", ""),
    "eb-pb-vbo-aL3": ("eb-pb-vbo", [('o', "PB-L3", 's'), ('i', "EB-post-out", 'e'), ('i', "EB-post-out", 'e'), ('o', "VBO-L", 'w')], "default", ""),
    # "eb-pb-vbo-aL1": ("eb-pb-vbo", [('o', "PB-L1", 's'), ('i', "EB-post-out", 'e'), ('i', "EB-post-out", 'e'), ('o', "VBO-L", 'w')], "default", ""),
    # large field fan
    "fan-1": ("fan", [('i', "VBO-R", 'e'), ('b', "FB-B", 's'),  ('b', "FB-B", 's'), ('b', "N-R2", 'n')], "default", "large field fan"),
    "fan-2": ("fan", [('i', "VBO-L", 'w'), ('b', "FB-G", 's'),  ('b', "FB-G", 's'), ('b', "N-L2", 'n')], "default", "large field fan"),
    # vbo-vbo
    "vbo-vbo-1": ("vbo-vbo", [('i', "VBO-L", 'w'), ('o', "VBO-R", 'e')], "default", ""),
    "vbo-vbo-2": ("vbo-vbo", [('i', "VBO-R", 'e'), ('o', "VBO-L", 'w')], "default", ""),
    # pb-eb-ltr (evens, inner, ant+post)
    "pb-eb-ltr-R6": ("pb-eb-ltr", [('i', "PB-R6", 's'), ('o', "EB-ant-in", 'w'), ('o', "EB-ant-in", 'w'), ('o', "LTR-R", 'e')], "default", ""),
    "pb-eb-ltr-R2": ("pb-eb-ltr", [('i', "PB-R2", 's'), ('o', "EB-ant-in", 'w'), ('o', "EB-ant-in", 'w'), ('o', "LTR-R", 'e')], "default", ""),
    "pb-eb-ltr-L6": ("pb-eb-ltr", [('i', "PB-L6", 's'), ('o', "EB-ant-in", 'e'), ('o', "EB-ant-in", 'e'), ('o', "LTR-L", 'w')], "default", ""),
    "pb-eb-ltr-L2": ("pb-eb-ltr", [('i', "PB-L2", 's'), ('o', "EB-ant-in", 'e'), ('o', "EB-ant-in", 'e'), ('o', "LTR-L", 'w')], "default", ""),
    "pb-eb-ltr-R8": ("pb-eb-ltr", [('i', "PB-R8", 's'), ('o', "EB-post-in", 'w'), ('o', "EB-post-in", 'w'), ('o', "LTR-R", 'e')], "default", ""),
    "pb-eb-ltr-R4": ("pb-eb-ltr", [('i', "PB-R4", 's'), ('o', "EB-post-in", 'w'), ('o', "EB-post-in", 'w'), ('o', "LTR-R", 'e')], "default", ""),
    "pb-eb-ltr-L8": ("pb-eb-ltr", [('i', "PB-L8", 's'), ('o', "EB-post-in", 'e'), ('o', "EB-post-in", 'e'), ('o', "LTR-L", 'w')], "default", ""),
    "pb-eb-ltr-L4": ("pb-eb-ltr", [('i', "PB-L4", 's'), ('o', "EB-post-in", 'e'), ('o', "EB-post-in", 'e'), ('o', "LTR-L", 'w')], "default", ""),
    # fb-no
    "fb-no-1": ("fb-no", [('b', "FB-A", 'w'), ('b', "N-R2", 'n'), ('b', "N-R2", 'n'), ('i', "VBO-R", 'e')], "default", "F1"),
    "fb-no-2": ("fb-no", [('b', "FB-H", 'e'), ('b', "N-L2", 'n'), ('b', "N-L2", 'n'), ('i', "VBO-L", 'w')], "default", "F1"),
    "fb-dlpc-1": ("fb-dlpc", [('b', "FB-A", 'w'), ('i', "DLPC-R", 's')], "default", "Fm1"),
    "fb-dlpc-2": ("fb-dlpc", [('b', "FB-H", 'e'), ('i', "DLPC-L", 's')], "default", "Fm1"),
    # of-ltr
    "OF-L-1": ("OF", [("i", "OF-L", 's'), ("o", "LTR-L", 'n')], "default", ""),
    "OF-R-1": ("OF", [("i", "OF-R", 's'), ("o", "LTR-R", 'n')], "default", ""),
    }
    

# ------------------------- region groups -------------------------
# purely cosmetic; we'll reuse "region" and use an appropriate style

regiongroups = {
    "PB": ("PB", ('box', (xc, pb.y, 16 * pb.width + groupbuffer, pb.height + groupbuffer)), "default-group-fill", ""),
    "FB": ("FB", ('box', (xc, fb.y, 8 * fb.width + groupbuffer, fb.height + groupbuffer)), "rose-group-fill", ""),
    "EB-anterior": ("anterior EB", ('box', (xc, (eb.antouty + eb.antiny) / 2, eb.width + groupbuffer, 2 * eb.height + groupbuffer)), "green-group-fill", ""),
    "EB-posterior": ("posterior EB", ('box', (xc, (eb.postiny + eb.postouty) / 2, eb.width + groupbuffer, 2 * eb.height + groupbuffer)), "green-group-fill", ""),
    "noduli": ("noduli", ('box', (xc, nn.y, 2 * nn.xoffset + 3 * nn.width + groupbuffer, nn.height + groupbuffer)), "brown-group-fill", ""),
    }

