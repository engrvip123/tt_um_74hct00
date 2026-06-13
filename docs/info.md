<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project is an open-source silicon re-implementation of the classic
**74HCT00 quad 2-input NAND** on the GlobalFoundries **gf180mcuD** PDK,
operating at **3.3 V**. Each of the four NAND gates is a CMOS gate with
**TTL-compatible (HCT) input thresholds** — `V_IL_max = 0.8 V` and
`V_IH_min = 2.0 V` — so the part can be driven directly by 3.3 V CMOS,
1.8 V GPIOs running open-drain with a pull-up, or a legacy TTL output.

Each gate is built bottom-up from four leaf cells:

```
nand2_hct  =  inv_skewed (A) ─┐
              inv_skewed (B) ─┴─►  nor2  ──►  inv_out  ──►  Y
```

The two front-end inverters are intentionally **skewed**
(`Wp ≪ Wn`) so they trip inside the HCT window rather than at VDD/2.
Combined with the NOR2 (De Morgan equivalent of NAND on the inverted inputs)
and a final ±4 mA output buffer, the gate meets the NXP 74HCT00 datasheet
specs on a 3.3 V rail. The HCT thresholds are TTL absolutes and do **not**
scale with VCC, so the same level-shifter window is exercised at 3.3 V as
at 5 V.

All four NAND gates share a common VDD/VSS rail pair routed across the
**1×2 analog tile** (346.64 × 325.36 µm). Outputs come out on the analog
pads `ua[0..3]` (not the digital `uo_out` bus) so the test bench can
measure VOH/VOL at the rated **±4 mA** drive without the TT pad buffer in
series. One extra analog pad, `ua[4]`, exposes the **A1 input node
directly** so the HCT trip window can be DC-swept on real silicon.

## How to test

External wiring:
- `VDPWR` → 3.3 V
- `VGND`  → 0 V
- `ui_in[0..7]` → gate inputs `A1, B1, A2, B2, A3, B3, A4, B4`
- `ua[0..3]`    → gate outputs `Y1, Y2, Y3, Y4`
- `ua[4]`       → A1 analog probe (shared with `ui_in[0]`;
   **do not drive both at once**)

Eight-section bench procedure:

1. **Truth table.** Drive each `(A_i, B_i)` pair through the four
   logic states `(0,0), (0,1), (1,0), (1,1)` with `ui_in` = 0 or 3.3 V.
   Verify `Y_i = NAND(A_i, B_i)` on `ua[0..3]` for all four gates.
2. **HCT input window — DC sweep.** Disconnect `ui_in[0]`, drive a slow
   DC ramp on `ua[4]` from 0 → 3.3 V (with `B1 = 3.3 V` so the gate's
   output follows A1). Capture `Y1` on `ua[0]`. The output must remain
   high for `V_in ≤ 0.8 V` and low for `V_in ≥ 2.0 V`.
3. **V_OUT at V_IL = 0.8 V.** Hold `ua[4] = 0.8 V`, `B1 = 3.3 V`. Read
   `ua[0]` (Y1). Expect `V_OH ≥ VCC − 0.1 V` (light load).
4. **V_OUT at V_IH = 2.0 V.** Hold `ua[4] = 2.0 V`, `B1 = 3.3 V`. Read
   `ua[0]`. Expect `V_OL ≤ 0.1 V`.
5. **Output drive — V_OH at −4 mA.** Force `(A1, B1) = (0, 1)` (output
   high). Sink 4 mA *out* of `ua[0]` with a current source. Measure
   `ua[0]`. Pass: `V_OH ≥ VCC − 0.66 V`.
6. **Output drive — V_OL at +4 mA.** Force `(A1, B1) = (1, 1)` (output
   low). Source 4 mA *into* `ua[0]`. Measure `ua[0]`. Pass:
   `V_OL ≤ 0.33 V`.
7. **Quiescent ICC.** Set all `ui_in` to valid CMOS levels (0 or 3.3 V),
   no load on `ua[0..3]`. Measure VDPWR current. Expect sub-µA.
8. **Propagation delay & 4-way matching.** Drive a square wave on each
   `A_i` with `B_i = 3.3 V`, observe the corresponding `ua[i]` on a
   scope. Report `t_PLH`, `t_PHL` for each gate and the gate-to-gate
   skew across all four NANDs.

## External hardware

- DC power supply (3.3 V, ≥ 50 mA capable)
- Source-measure unit or precision DMM + sourcing supply for the `ua[4]`
  DC ramp (steps of ≤ 50 mV across the 0.8–2.0 V window)
- Programmable current source (or load board with a 4 mA sink/source
  switch) for the V_OH / V_OL drive tests
- Function generator (square-wave, 0 – 3.3 V swing) for propagation
  delay
- Oscilloscope with ≥ 100 MHz analog bandwidth for `t_PLH` / `t_PHL`
- DMM with µA-range capability for the quiescent ICC measurement

No PMOD, LED display, or other digital accessory boards are required.
