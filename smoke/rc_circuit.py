#!/usr/bin/env python3
"""
Trivial RC low-pass network, defined code-first with SKiDL.

    V1 (AC/PULSE source) --+
                            |
                            R1 (1k)
                            |
                           OUT----+
                            |     |
                            C1 (100n)
                            |     |
                           GND---+

Run with the SKiDL venv interpreter:
  /Users/roberto/EDA/env/venv/bin/python3 /Users/roberto/EDA/smoke/rc_circuit.py

Requires KiCad symbol/footprint dirs to be set (KiCad 10 ships as kicad9-era
skidl constant "KICAD9" - see notes in smoke/NOTES.md).
"""
import os

for _ver in ("6", "7", "8", "9", "10"):
    os.environ.setdefault(
        f"KICAD{_ver}_SYMBOL_DIR",
        "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/symbols",
    )
    os.environ.setdefault(
        f"KICAD{_ver}_FOOTPRINT_DIR",
        "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints",
    )

from skidl import Part, Net, generate_netlist, generate_schematic, ERC, TEMPLATE, POWER

OUT_DIR = "/Users/roberto/EDA/smoke"

# --- Parts -----------------------------------------------------------
r1 = Part("Device", "R", value="1k", footprint="Resistor_SMD:R_0805_2012Metric")
c1 = Part("Device", "C", value="100n", footprint="Capacitor_SMD:C_0805_2012Metric")

# A SPICE-only voltage source symbol (KiCad 10 ngspice-model symbol) so the
# schematic/netlist has a driver. VPULSE gives a clean 0->1V step at t=0 so we
# can verify the RC time constant tau = R*C from a .tran simulation.
# Give it a real 2-pin footprint (stand-in for an edge connector where the
# stimulus would physically be injected) so the KiCad netlist -> PCB path
# has something concrete to place, instead of leaving footprint empty
# (which SKiDL's kicad10 netlist generator treats as a hard error).
v1 = Part(
    "Simulation_SPICE",
    "VPULSE",
    footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
)
v1.fields["Sim.Params"] = "y1=0 y2=1 td=0 tr=1n tf=1n tw=10m per=20m"
# WORKAROUND: SKiDL's generate_schematic() does not copy the "Sim.Type" /
# "Sim.Device" properties from the library symbol definition into the
# .kicad_sch lib_symbols cache (confirmed by inspecting the generated file -
# only Sim.Params survives). Without these, kicad-cli's
# `sch export netlist --format spice` cannot tell this is a PULSE source and
# falls back to a broken `dc="VPULSE"` line. Setting them explicitly here
# works around the gap.
v1.fields["Sim.Type"] = "PULSE"
v1.fields["Sim.Device"] = "V"

# --- Nets --------------------------------------------------------------
vin = Net("VIN")
vout = Net("OUT")
gnd = Net("GND")
gnd.drive = POWER

# V1: pin 1 = +, pin 2 = - (per Simulation_SPICE VSOURCE symbol)
v1["1"] += vin
v1["2"] += gnd

r1[1] += vin
r1[2] += vout

c1[1] += vout
c1[2] += gnd

if __name__ == "__main__":
    print("Parts:", [p.ref for p in [r1, c1, v1]])
    print("Nets:", [n.name for n in [vin, vout, gnd]])

    erc_ok = True
    try:
        ERC()
    except Exception as e:
        erc_ok = False
        print("SKiDL ERC raised:", e)

    # 1) KiCad-format netlist (native SKiDL output, used for kinet2pcb / KiCad import)
    kicad_net_path = os.path.join(OUT_DIR, "rc_circuit.net")
    generate_netlist(file_=kicad_net_path, tool="kicad10")
    print("Wrote KiCad netlist:", kicad_net_path)

    # 2) SPICE-format netlist
    try:
        spice_net_path = os.path.join(OUT_DIR, "rc_circuit.cir")
        generate_netlist(file_=spice_net_path, tool="spice")
        print("Wrote SPICE netlist:", spice_net_path)
    except Exception as e:
        print("SPICE netlist generation FAILED:", repr(e))

    # 3) KiCad schematic (.kicad_sch)
    try:
        generate_schematic(file_=os.path.join(OUT_DIR, "rc_circuit"))
        print("generate_schematic() completed without exception")
    except Exception as e:
        print("generate_schematic() FAILED:", repr(e))
