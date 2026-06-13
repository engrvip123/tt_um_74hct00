/*
 * Copyright (c) 2026 Vipul Sharma
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_74hct00 (
    input  wire       VGND,
    input  wire       VDPWR,    // 3.3v core power supply
//    input  wire       VAPWR,    // second analog power supply (VAA)
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    inout  wire [7:0] ua,       // Analog pins, only ua[5:0] can be used
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Analog macro: the NAND functionality lives in the gf180mcuD GDS, not in
  // Verilog. ui_in[7:0] are routed to the four gate input pairs (A1/B1..A4/B4),
  // ua[3:0] carry Y1..Y4, and ua[4] is the HCT-window probe on the A1 node.
  // The digital uo_out / uio_* paths are unused and tied off here.
  assign uo_out  = 8'b0;
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  // Suppress unused-input lint warnings (these nets are physical on the GDS
  // even though the Verilog wrapper does not reference them).
  wire _unused = &{ena, clk, rst_n, uio_in, ui_in, ua, VDPWR, VGND, 1'b0};

endmodule
