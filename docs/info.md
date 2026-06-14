## How it works

This project is an open-source silicon implementation of **quad
2-input NAND** on the GlobalFoundries **gf180mcuD** process, operating from a
**3.3 V** supply. Each NAND gate presents a TTL-compatible input window
(V<sub>IL,max</sub> = 0.8 V, V<sub>IH,min</sub> = 2.0 V) and is sized for
**±4 mA** drive at the output.

The HCT input behaviour is realised through a skewed-inverter / NOR2 /
output-buffer chain rather than a plain CMOS NAND topology:

```
nand2_hct  =  inv_skewed (A) ─┐
              inv_skewed (B) ─┴─►  nor2  ──►  inv_out  ──►  Y
```

The four NAND gates share a common V<sub>DD</sub>/V<sub>SS</sub> rail pair.
Each gate output is routed to an analog pin in `ua[0..3]` rather than to the
digital pins, allowing V<sub>OH</sub> and V<sub>OL</sub> to be measured at
the rated ±4 mA drive without the digital output buffer of the TT pad frame
in series.

## Schematics

The design was captured in **xschem** and simulated in **ngspice**. Per-cell
LVS was performed in KLayout.

Chip-level testbench (`tb_74hct00_top.sch`):

![Chip-level testbench](tb_74hct00_top.png)

Top-level schematic (`74hct00_top.sch`):

![Chip top](74hct00_top.png)

NAND gate (`nand2_hct.sch`):

![NAND gate](nand2_hct.png)

Interior NOR2 (`nor2.sch`):

![Interior NOR2](nor2.png)

## How to test

The procedure below is a basic functional verification of all four NAND gates.

1. Apply **3.3 V** between `VDPWR` and `VGND`.
2. For each gate *i* ∈ {1, 2, 3, 4}, drive the two input pins
   (A<sub>i</sub> on `ui_in[2i−2]`, B<sub>i</sub> on `ui_in[2i−1]`) to
   either 0 V or 3.3 V and read the corresponding output Y<sub>i</sub> on
   `ua[i−1]`. The output must follow the NAND truth table:

   | A | B | Y |
   |---|---|---|
   | 0 | 0 | 1 |
   | 0 | 1 | 1 |
   | 1 | 0 | 1 |
   | 1 | 1 | 0 |

3. *(Optional)* **HCT input-window check.** Disconnect `ui_in[0]` and apply
   a slow DC ramp on `ua[4]` from 0 V to 3.3 V while holding B<sub>1</sub>
   (`ui_in[1]`) at 3.3 V. Observe Y<sub>1</sub> on `ua[0]`. The output must
   remain at logic high for V<sub>in</sub> ≤ 0.8 V and must be at logic low
   for V<sub>in</sub> ≥ 2.0 V.

Note: `ui_in[0]` and `ua[4]` are connected to the same internal
A<sub>1</sub> node and must not be driven simultaneously.

## External hardware

- 3.3 V DC power supply (≥ 50 mA capable).
- Digital multimeter for output-voltage measurement.
- (Optional) Variable low-voltage DC source for the HCT input-window check.
