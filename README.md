![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg)

# 74HCT00 Quad 2-Input NAND — 3.3 V Open-Source Re-implementation

An open-source silicon re-implementation of the classic **74HCT00 quad
2-input NAND** logic IC, ported to the GlobalFoundries **gf180mcuD** PDK
at **3.3 V**. 

- [Read information about this project](docs/info.md)

## Why this design

The 74HCT00 family is a classic TTL-compatible CMOS NAND part that
boards have relied on for decades to translate TTL-level signals into
CMOS logic (V_IL_max = 0.8 V, V_IH_min = 2.0 V). Addressing the obsolescence 
of 74HCT-family logic, this project tries to provides an open-source replacement. 

The design is a fully custom analog layout (no
standard-cell synthesis): four NAND gates built from a circuit chain that preserves the HCT
threshold window on a 3.3 V rail and drives a rated **±4 mA load
current** at the output.

## Pinout (Tiny Tapeout side)

All four gate **outputs (Y1..Y4) come out on analog pads `ua[0..3]`**,
not on the digital `uo_out` bus, so the bench can measure VOH/VOL at
the rated ±4 mA drive without the TT pad buffer in series. The A input
of gate 1 (A1) is on the analog pad `ua[4]` — used both for functional
drive (0 / 3.3 V truth-table test) and for a slow DC ramp characterising
the HCT input window on silicon. Driving A1 through a digital `ui_in`
pin would defeat the HCT-window measurement, since the TT pad buffer
snaps any intermediate voltage to a clean 0 / 3.3 V at its own CMOS
threshold before reaching the gate. The remaining seven gate inputs
(B1, A2 / B2, A3 / B3, A4 / B4) come in on `ui_in[1..7]`; `ui_in[0]`
is left unused.

See [docs/info.md](docs/info.md) for the full pin table and the bench measurement procedure. 
