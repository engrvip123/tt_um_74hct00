#!/usr/bin/env python3
"""
Build the TT-GF shuttle wrapper cell `tt_um_74hct00`.

Reads ../gds/74hct00_top.gds and routes its 14 pins to TT-GF tile pads:

  Y1..Y4               -> ua[0..3]      (analog pads, bottom of tile)
  A1..A4, B1..B4       -> ui_in[0..7]   (digital pads, top of tile, gate-paired)
  A1 (extra)           -> ua[4]         (HCT-window analog probe)
  VDD bus              -> VDPWR M1 stripe (top edge of tile)
  VSS bus              -> VGND  M1 stripe (bottom edge of tile)

Routing discipline (per user 2026-06-13):
  No top-level M3/M4 wires cross horizontally over the core 74hct00_top cell.
  Each pin exits the cell through its NEAREST cell-bbox edge with just enough
  vertical M4 stub to clear the bbox; all further routing runs on dedicated
  M4 channels OUTSIDE the cell bbox, going AROUND the cell when source and
  destination are on opposite sides.

Run:  cd /foss/designs/tt_um_74hct00/src
      klayout -b -r build_tt_um_74hct00.py
"""

import pya
import os, sys

# ---- gf180mcuD layers ----------------------------------------------------
L = {
    "metal1":   (34, 0),   "m1_label": (34, 10),
    "via1":     (35, 0),
    "metal2":   (36, 0),   "m2_label": (36, 10),
    "via2":     (38, 0),
    "via3":     (40, 0),
    "metal3":   (42, 0),   "m3_label": (42, 10),
    "metal4":   (46, 0),   "m4_label": (46, 10),
}

# ---- tile geometry (from def/tt_analog_1x2.def) --------------------------
TILE_W = 346.640
TILE_H = 325.360

UA_X    = [327.320, 283.640, 239.960, 196.280, 152.600, 108.920, 65.240, 21.560]
UA_W, UA_H, UA_Y_C = 3.000, 1.000, 0.500

UI_X    = [316.680, 309.400, 302.120, 294.840, 287.560, 280.280, 273.000, 265.720]
UI_W, UI_H, UI_Y_C = 0.300, 1.000, 324.860

# ---- 74hct00_top pin positions in CELL-LOCAL frame -----------------------
NH_A_X, NH_A_Y = 0.49, 5.25
NH_B_X, NH_B_Y = 8.49, 5.25
NH_Y_X, NH_Y_Y = 43.70, 7.30
X_SEP = 50.0
Y_SEP = 30.0
INSTANCES = [(0.0, 0.0), (X_SEP, 0.0), (0.0, Y_SEP), (X_SEP, Y_SEP)]

CELL_VDD_BUS_X     = -6.950
CELL_VSS_BUS_X     = +99.410
CELL_VDD_BUS_TOP_Y = +55.640
CELL_VSS_BUS_BOT_Y =  -3.300
CELL_BBOX_X_MIN    = -10.950
CELL_BBOX_X_MAX    = +103.910
CELL_BBOX_Y_MIN    =  -3.300
CELL_BBOX_Y_MAX    = +55.640

# ---- wrapper placement: cell centred horizontally in tile, mid-height ----
CELL_X = 116.0
CELL_Y = 100.0

CELL_LEFT  = CELL_X + CELL_BBOX_X_MIN     # 105.05
CELL_RIGHT = CELL_X + CELL_BBOX_X_MAX     # 219.91
CELL_BOT   = CELL_Y + CELL_BBOX_Y_MIN     # 96.70
CELL_TOP   = CELL_Y + CELL_BBOX_Y_MAX     # 155.64

# ---- routing geometry ---------------------------------------------------
W_M4         = 0.50
VIA_SIZE     = 0.260
VIA_MENC     = 0.380
VIA_SPACE    = 0.260
VIA_PITCH    = VIA_SIZE + VIA_SPACE
M4_SPACE     = 0.40
CH_PITCH     = W_M4 + M4_SPACE   # 0.90 um pitch between parallel channels

# Channels below the cell (y in [VGND+margin, CELL_BOT-margin])
def channels_below(n, start_y=88.0, step=-CH_PITCH):
    return [start_y + i * step for i in range(n)]

def channels_above(n, start_y=162.0, step=CH_PITCH):
    return [start_y + i * step for i in range(n)]

def channels_right(n, start_x=222.0, step=CH_PITCH):
    return [start_x + i * step for i in range(n)]

def channels_left(n, start_x=104.0, step=-CH_PITCH):
    return [start_x + i * step for i in range(n)]

VDPWR_Y    = 322.000
VGND_Y     =   3.000
W_PWR_RAIL = 4.000

# ---- layout setup -------------------------------------------------------
ly = pya.Layout()
ly.dbu = 0.001
def L_(name): return ly.layer(*L[name])

macro_path = "../gds/74hct00_top.gds"
if not os.path.exists(macro_path):
    raise SystemExit(f"Macro not found: {macro_path}")
ly.read(macro_path)
hct = ly.cell("74hct00_top")
assert hct, "74hct00_top cell not found after reading"

top = ly.create_cell("tt_um_74hct00")
top.insert(pya.CellInstArray(hct.cell_index(),
    pya.Trans(int(round(CELL_X/ly.dbu)), int(round(CELL_Y/ly.dbu)))))

# ---- helpers ------------------------------------------------------------
def box(layer, x0, y0, x1, y1):
    top.shapes(L_(layer)).insert(pya.DBox(min(x0,x1), min(y0,y1),
                                          max(x0,x1), max(y0,y1)))

def label(name, x, y, layer):
    top.shapes(L_(layer)).insert(pya.DText(name, pya.DTrans(x, y)))

def m_h(layer, x0, x1, y, w=W_M4):
    box(layer, x0, y - w/2, x1, y + w/2)

def m_v(layer, x, y0, y1, w=W_M4):
    box(layer, x - w/2, y0, x + w/2, y1)

def via_tower(x, y):
    half_p = VIA_MENC / 2
    for m in ("metal1", "metal2", "metal3", "metal4"):
        box(m, x - half_p, y - half_p, x + half_p, y + half_p)
    half_v = VIA_SIZE / 2
    for v in ("via1", "via2", "via3"):
        box(v, x - half_v, y - half_v, x + half_v, y + half_v)

# ---- 1. Pad pins at ua[*] and ui_in[*] on Metal4 ------------------------
for i, ux in enumerate(UA_X):
    box("metal4", ux - UA_W/2, UA_Y_C - UA_H/2, ux + UA_W/2, UA_Y_C + UA_H/2)
    label(f"ua[{i}]", ux, UA_Y_C, "m4_label")

for i, ux in enumerate(UI_X):
    box("metal4", ux - UI_W/2, UI_Y_C - UI_H/2, ux + UI_W/2, UI_Y_C + UI_H/2)
    label(f"ui_in[{i}]", ux, UI_Y_C, "m4_label")

# ---- compute cell pin world positions -----------------------------------
def gate_pin(ab, gate_idx):
    xo, yo = INSTANCES[gate_idx]
    if ab == "A":  return (CELL_X + NH_A_X + xo, CELL_Y + NH_A_Y + yo)
    return (CELL_X + NH_B_X + xo, CELL_Y + NH_B_Y + yo)

Y_PIN = [(CELL_X + NH_Y_X + xo, CELL_Y + NH_Y_Y + yo) for (xo, yo) in INSTANCES]

# ---- 2. Y1, Y2 (bottom row) -> ua[0], ua[1] -- exit BOTTOM, channel below
Y_BELOW_CH = channels_below(2)
for i in (0, 1):
    yx, yy = Y_PIN[i]
    ua_x   = UA_X[i]
    ch_y   = Y_BELOW_CH[i]
    via_tower(yx, yy)
    m_v("metal4", yx,   ch_y,  yy)
    m_h("metal4", yx,   ua_x, ch_y)
    m_v("metal4", ua_x, ch_y, UA_Y_C + UA_H/2)

# ---- 3. Y3, Y4 (top row) -> ua[2], ua[3] -- exit TOP, around RIGHT side
Y_ABOVE_CH = channels_above(2)
Y_RIGHT_VC = channels_right(2)
Y_BELOW2   = channels_below(2, start_y=86.2)
for k, i in enumerate((2, 3)):
    yx, yy = Y_PIN[i]
    ua_x   = UA_X[i]
    ch_above = Y_ABOVE_CH[k]
    vc_right = Y_RIGHT_VC[k]
    ch_below = Y_BELOW2[k]
    via_tower(yx, yy)
    m_v("metal4", yx,       yy,       ch_above)
    m_h("metal4", yx,       vc_right, ch_above)
    m_v("metal4", vc_right, ch_below, ch_above)
    m_h("metal4", vc_right, ua_x,     ch_below)
    m_v("metal4", ua_x,     ch_below, UA_Y_C + UA_H/2)

# ---- 4. Top-row inputs A3..B4 -> ui_in[4..7] -- direct UP --------------
TOP_INPUTS = [("A", 2, 4), ("B", 2, 5), ("A", 3, 6), ("B", 3, 7)]
TOP_IN_ABOVE_CH = channels_above(4, start_y=164.0)
for k, (ab, g, ui_idx) in enumerate(TOP_INPUTS):
    px, py = gate_pin(ab, g)
    ui_x   = UI_X[ui_idx]
    ch_y   = TOP_IN_ABOVE_CH[k]
    via_tower(px, py)
    m_v("metal4", px,   py,   ch_y)
    m_h("metal4", px,   ui_x, ch_y)
    m_v("metal4", ui_x, ch_y, UI_Y_C - UI_H/2)

# ---- 5. Bottom-row inputs A1..B2 -> ui_in[0..3] -- around LEFT side -----
BOT_INPUTS = [("A", 0, 0), ("B", 0, 1), ("A", 1, 2), ("B", 1, 3)]
BOT_IN_BELOW_CH = channels_below(4, start_y=82.0)
BOT_IN_LEFT_VC  = channels_left(4, start_x=103.0)
BOT_IN_ABOVE_CH = channels_above(4, start_y=169.0)
for k, (ab, g, ui_idx) in enumerate(BOT_INPUTS):
    px, py = gate_pin(ab, g)
    ui_x   = UI_X[ui_idx]
    ch_below = BOT_IN_BELOW_CH[k]
    vc_left  = BOT_IN_LEFT_VC[k]
    ch_above = BOT_IN_ABOVE_CH[k]
    via_tower(px, py)
    m_v("metal4", px,      ch_below, py)
    m_h("metal4", px,      vc_left,  ch_below)
    m_v("metal4", vc_left, ch_below, ch_above)
    m_h("metal4", vc_left, ui_x,     ch_above)
    m_v("metal4", ui_x,    ch_above, UI_Y_C - UI_H/2)

# ---- 6. A1 extra HCT probe -> ua[4] -- direct DOWN, channel BELOW -------
a1_x, a1_y = gate_pin("A", 0)
ua4_x      = UA_X[4]
HCT_CH_Y   = 70.0
m_v("metal4", a1_x,  HCT_CH_Y, a1_y)
m_h("metal4", a1_x,  ua4_x,    HCT_CH_Y)
m_v("metal4", ua4_x, HCT_CH_Y, UA_Y_C + UA_H/2)

# ---- 7. VDPWR / VGND M1 stripes -----------------------------------------
box("metal1", 0, VDPWR_Y - W_PWR_RAIL/2, TILE_W, VDPWR_Y + W_PWR_RAIL/2)
box("metal1", 0, VGND_Y  - W_PWR_RAIL/2, TILE_W, VGND_Y  + W_PWR_RAIL/2)
label("VDPWR", TILE_W/2, VDPWR_Y, "m1_label")
label("VGND",  TILE_W/2, VGND_Y,  "m1_label")

# ---- 8. Cell VDD/VSS buses -> tile power stripes -----------------------
vdd_bus_x = CELL_X + CELL_VDD_BUS_X
vdd_top_y = CELL_Y + CELL_VDD_BUS_TOP_Y
W_PWR_STUB = 8.0
m_v("metal1", vdd_bus_x, vdd_top_y, VDPWR_Y + W_PWR_RAIL/2, w=W_PWR_STUB)

vss_bus_x = CELL_X + CELL_VSS_BUS_X
vss_bot_y = CELL_Y + CELL_VSS_BUS_BOT_Y
m_v("metal1", vss_bus_x, VGND_Y - W_PWR_RAIL/2, vss_bot_y, w=W_PWR_STUB)

# ---- 9. M1 snap to 5 nm grid -------------------------------------------
GRID_NM = 5
def snap_m1_in_all_cells(layout, grid_nm=GRID_NM):
    li = layout.find_layer(34, 0)
    if li is None: return 0
    fixed = 0
    for cell in layout.each_cell():
        rep = []
        for sh in cell.shapes(li).each():
            p = sh.polygon
            need = False
            for e in p.each_edge():
                if (e.p1.x % grid_nm or e.p1.y % grid_nm or
                    e.p2.x % grid_nm or e.p2.y % grid_nm):
                    need = True; break
            if need:
                pts = []; seen = set()
                for e in p.each_edge():
                    for q in (e.p1, e.p2):
                        sx = round(q.x / grid_nm) * grid_nm
                        sy = round(q.y / grid_nm) * grid_nm
                        if (sx, sy) not in seen:
                            seen.add((sx, sy))
                            pts.append(pya.Point(sx, sy))
                rep.append((sh, pya.Polygon(pts)))
        for sh, newp in rep:
            cell.shapes(li).erase(sh)
            cell.shapes(li).insert(newp)
            fixed += 1
    return fixed

_snapped = snap_m1_in_all_cells(ly)
print(f"Snapped {_snapped} offgrid M1 shapes to {GRID_NM} nm grid")

# ---- 10. Write ----------------------------------------------------------
OUTPUT = "../gds/tt_um_74hct00.gds"
ly.write(OUTPUT)
bb = top.bbox()
print(f"Wrote {OUTPUT}")
print(f"Cell:  W x H = {bb.width()*ly.dbu:.2f} x {bb.height()*ly.dbu:.2f} um")
print(f"74hct00_top instance bbox in tile frame:  "
      f"x=[{CELL_LEFT:.2f}, {CELL_RIGHT:.2f}]  y=[{CELL_BOT:.2f}, {CELL_TOP:.2f}]")
print(f"Tile DIEAREA: {TILE_W:.2f} x {TILE_H:.2f} um")
