"""
coupon_specs.py - physical specifications of the P370 plug-and-play coupon set.

Plain constants only: no imports, no functions, no I/O. Every value carries a
comment naming its source:

    [guide]    kit user guide rev 1.0 (2018-02-21): body text, the stack-up
               figure (fig. 2) and the via figure (fig. 3)
    [ds]       kit datasheet, 2022 edition
    [dxf:NN]   measured with ezdxf from the vendor DXF for part 907-000-10NN
               ($INSUNITS = 1, i.e. inches; converted to metres here).
               [dxf:all] means the value is identical in all nine files.
    [rogers]   Rogers Corporation data sheets for RO4003C/RO4350B and
               RO4450F/RO4460G2, downloaded 2026-09-08 into
               ./reference_collaterals/ (git-ignored), cross-checked against
               the Rogers product pages. NOT part of the kit collateral:
               neither the guide nor the kit datasheet states Dk or Df.

Where the DXF and the documents disagree, both values are kept and the
constant name says which is which. See DISCREPANCIES at the bottom.

The reference documents and DXF files are vendor material and are not
redistributed with this repository. Only the dimensions and material facts
extracted from them appear here.

Units: SI (metres, hertz, ohms) unless the name ends in _MIL, _MM, _GHZ, _OZ
or _PS. Source numbers are kept visible as `<value> * MIL` / `* INCH`.
"""

# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------
MIL = 25.4e-6        # m
INCH = 25.4e-3       # m
MM = 1e-3            # m

# ---------------------------------------------------------------------------
# Stack-up                                                    [guide] fig. 2
# ---------------------------------------------------------------------------
STACKUP_LAYER_COUNT = 4                       # [guide] fig. 2
STACKUP_TOTAL_THICKNESS = 61.54 * MIL         # [guide] fig. 2; equals the sum of the rows below

# Top to bottom. Copper thicknesses are *finished* (base foil plus plating);
# dielectric thicknesses are the pressed dielectric only. Tolerances as drawn.
# Fields: (name, kind, material, thickness, tolerance, note)
STACKUP = (
    ("L01", "copper",     "Cu, 0.5 oz base",  2.10 * MIL, 0.2 * MIL, "top signal; finished incl. plating"),          # [guide] fig. 2
    ("D1",  "dielectric", "RO4003C core",     8.00 * MIL, 1.0 * MIL, "0.5/0.5 oz clad core; substrate of the L01 microstrip"),  # [guide] fig. 2
    ("L02", "copper",     "Cu, 0.5 oz base",  0.67 * MIL, 0.2 * MIL, "ground"),                                     # [guide] fig. 2
    ("D2",  "dielectric", "RO4450F prepreg",  4.00 * MIL, 1.0 * MIL, ""),                                           # [guide] fig. 2
    ("D3",  "dielectric", "RO4003C core",    32.00 * MIL, 1.0 * MIL, "unclad (0.0/0.0 oz) core"),                   # [guide] fig. 2
    ("D4",  "dielectric", "RO4450F prepreg",  4.00 * MIL, 1.0 * MIL, ""),                                           # [guide] fig. 2
    ("L03", "copper",     "Cu, 0.5 oz base",  0.67 * MIL, 0.2 * MIL, "ground"),                                     # [guide] fig. 2
    ("D5",  "dielectric", "RO4003C core",     8.00 * MIL, 1.0 * MIL, "0.5/0.5 oz clad core; substrate of the L04 microstrip"),  # [guide] fig. 2
    ("L04", "copper",     "Cu, 0.5 oz base",  2.10 * MIL, 0.2 * MIL, "bottom signal/ground; finished incl. plating"),  # [guide] fig. 2
)

# Convenience aliases for the microstrip synthesis
H_SUB = 8.0 * MIL            # [guide] fig. 2 - dielectric under the L01 (and L04) trace.
                             # [dxf:all] top silkscreen reads "8 RO4003": agrees.
T_CU_OUTER = 2.1 * MIL       # [guide] fig. 2 - finished outer copper (0.5 oz base + plating)
T_CU_INNER = 0.67 * MIL      # [guide] fig. 2 - finished inner copper
CU_BASE_OZ = 0.5             # [guide] fig. 2 - base foil weight, all four layers

PLATING = "NiAu"             # [guide] p. 4
PLATING_AU_MIN_AS_STATED = 75e-6   # m  [guide] p. 4 states a 75 um minimum gold thickness.
                                   # FLAG: not credible for a Ni/Au finish (that is 3 mil of gold);
                                   # 75 uin = 1.9 um is the likely intent. Recorded verbatim; do not use blindly.

COPPER_ROUGHNESS = None      # Not stated anywhere in the collateral. Synthesis must choose
                             # and document its own value; do not attribute one to the kit.

# ---------------------------------------------------------------------------
# Material                                                        [rogers]
# ---------------------------------------------------------------------------
MATERIAL_CORE = "RO4003C"    # [guide] p. 4 says "Rogers 4003"; RO4003C is the current Rogers
                             # designation. Not RO4350B; see the CLAUDE.md material invariant.
MATERIAL_PREPREG = "RO4450F" # [guide] fig. 2

RO4003C_DK_PROCESS = 3.38        # [rogers] IPC-TM-650 2.5.5.5 clamped stripline, 10 GHz, 23 C
RO4003C_DK_PROCESS_TOL = 0.05    # [rogers]
RO4003C_DK_DESIGN = 3.55         # [rogers] differential phase length method, quoted for 8 to 40 GHz;
                                 # the value Rogers recommends for impedance / phase modelling of
                                 # built circuits (lot average, most common thicknesses)
RO4003C_DK_DESIGN_F_RANGE = (8e9, 40e9)   # Hz [rogers]
RO4003C_DF = 0.0027              # [rogers] 10 GHz, 23 C
RO4003C_F_REF = 10e9             # Hz [rogers] reference frequency for the process Dk and Df

RO4450F_DK = 3.52                # [rogers] IPC-TM-650 2.5.5.5, 10 GHz, 23 C
RO4450F_DK_TOL = 0.05            # [rogers]
RO4450F_DF = 0.0040              # [rogers] 10 GHz, 23 C
RO4450F_F_REF = 10e9             # Hz [rogers]
RO4450F_SHEET_THICKNESS = 4.0 * MIL   # [rogers] standard sheet 0.0040 in +/- 0.0006 in; the stack-up's
                                      # 4 mil prepreg layers are one sheet each

# Which Dk the synthesis uses (process vs design) is a modelling decision that
# is deliberately NOT made here.

# ---------------------------------------------------------------------------
# Board outline and trace geometry common to all coupons          [dxf:all]
# ---------------------------------------------------------------------------
BOARD_WIDTH = 0.709 * INCH               # [dxf:all] 18.01 mm (18 mm design intent)
BOARD_LENGTH_6CM = 2.362 * INCH          # [dxf:40-47] 59.99 mm (60 mm design intent); silkscreen "2.362" agrees
BOARD_LENGTH_3CM = 1.181 * INCH          # [dxf:48] 30.00 mm
TRACE_CENTRELINE_Y = 0.3545 * INCH       # [dxf:all] trace on the board's long axis of symmetry

W_TRACE_50 = 17.3 * MIL      # [guide] p. 4 "design trace width 17.3 mil".
                             # [dxf:40,41,42,43,44,45,48] L01 polyline height 0.0173 in: agrees.
W_TRACE_105 = 19.0 * MIL     # [dxf:46,47] L01 polyline height 0.0190 in; silkscreen "W19".
                             # The guide gives no width for this board.

# Connector launch: the trace narrows to 11 mil at the board edge and tapers
# linearly to full width over the first 50 mil. Same on every board; the
# silkscreen encodes it as "W17.3 11-50" / "W19 11-50".
W_LAUNCH_EDGE = 11.0 * MIL   # [dxf:all]
L_LAUNCH_TAPER = 50.0 * MIL  # [dxf:all]

# Coplanar ground pads on L01 at each board end, both sides of the trace
LAUNCH_GND_PAD_LENGTH = 0.206 * INCH     # [dxf:all] from the board edge inward
LAUNCH_GND_PAD_HALF_SPAN = 0.250 * INCH  # [dxf:all] centreline to the pad's outer edge
LAUNCH_CPW_GAP_AT_EDGE = 5.5 * MIL       # [dxf:all] pad edge to 11-mil trace edge at x = 0
LAUNCH_CPW_LENGTH = 30.0 * MIL           # [dxf:all] ground stays close for 30 mil (chamfer begins at 20 mil)
LAUNCH_GND_SETBACK = 65.0 * MIL          # [dxf:all] pad edge to trace centreline for the rest of the pad

# Ground vias at each board end, mirrored about the centreline (6 per end).
# Fields: (x from board edge, |y| from centreline, drill diameter)
LAUNCH_GND_VIAS = (
    (0.011 * INCH, 21.0 * MIL,  8.0 * MIL),   # [dxf:all]
    (0.015 * INCH, 43.0 * MIL, 12.0 * MIL),   # [dxf:all]
    (0.015 * INCH, 68.0 * MIL, 12.0 * MIL),   # [dxf:all]
)

MOUNT_HOLE_D = 80.0 * MIL                # [dxf:all] non-plated, 4 per board
MOUNT_HOLE_X_FROM_END = 0.110 * INCH     # [dxf:all]
MOUNT_HOLE_Y_FROM_CENTRELINE = 0.1875 * INCH   # [dxf:all] +/-

# Ground planes
PLANE_PULLBACK_LONG_EDGE = 15.0 * MIL    # [dxf:all] L02, L03, L04 stop 15 mil short of both long edges
PLANE_L03_PULLBACK_END = 30.0 * MIL      # [dxf:all] L03 also stops 30 mil short of each board end;
                                         # L02 and L04 run to the board ends

# ---------------------------------------------------------------------------
# Via structure, 2-via fixtures                       [guide] fig. 3, [dxf:44,45]
# ---------------------------------------------------------------------------
# Signal path: L01 for 20 mm, through-via to L04 for 20 mm, through-via back
# to L01 for 20 mm. Both vias are full through-vias (no stub).
VIA_X_FROM_PORT1 = (0.7875 * INCH, 1.5745 * INCH)        # [dxf:44,45] 20.00 mm and 40.00 mm
VIA_FIXTURE_SECTIONS = (                                  # [dxf:44,45]; [ds] "top, bottom, top again"
    (20.0 * MM, "L01"),
    (20.0 * MM, "L04"),
    (20.0 * MM, "L01"),
)
VIA_LENGTH = STACKUP_TOTAL_THICKNESS                      # through-via L01 -> L04
VIA_FIXTURE_L04_GND_ONLY_UNDER_CONNECTORS = True          # [dxf:44,45] L04 carries the trace plus ground
                                                          # rectangles within LAUNCH_GND_PAD_LENGTH of
                                                          # each end; no full bottom plane

# Signal via - DXF values
VIA_DRILL_DXF = 10.0 * MIL       # [dxf:44,45] PLATED-layer circle diameter
VIA_PAD_DXF = 20.0 * MIL         # [dxf:44,45] L01 and L04 pad circle diameter
VIA_ANTIPAD_DXF = 30.0 * MIL     # [dxf:44,45] L02 and L03 cut-out diameter, same on both planes

# Signal via - user-guide values.  FLAG: all four differ from the DXF.
VIA_DRILL_GUIDE = 13.0 * MIL              # [guide] fig. 3, +/- 1 mil
VIA_DRILL_GUIDE_TOL = 1.0 * MIL           # [guide] fig. 3
VIA_PAD_GUIDE = 23.0 * MIL                # [guide] fig. 3
VIA_ANTIPAD_TL_GND_GUIDE = 46.0 * MIL     # [guide] fig. 3 "transmission line ground antipad", +/- 1 mil
VIA_ANTIPAD_OTHER_GND_GUIDE = 52.0 * MIL  # [guide] fig. 3 "all other ground antipad", +/- 1 mil
VIA_ANTIPAD_GUIDE_TOL = 1.0 * MIL         # [guide] fig. 3

# Ground vias around each signal via
VIA_GND_COUNT = 4                     # [guide] fig. 3 "5 places" = 1 signal + 4 ground; [dxf:44,45] agree
VIA_GND_OFFSET = 22.0 * MIL           # [dxf:44,45] at (+/-22, +/-22) mil from the signal via centre
VIA_GND_DRILL_DXF = VIA_DRILL_DXF     # [dxf:44,45] same drill and pad as the signal via
VIA_GND_PAD_DXF = VIA_PAD_DXF         # [dxf:44,45]
VIA_GND_CLEARANCE_R = 15.0 * MIL      # [dxf:44,45] trace edge is notched on a 15 mil radius around
                                      # the two ground vias it passes (5 mil clearance to the pad)
# Ground vias have no antipad on L02/L03, so they tie all four copper layers.  [dxf:44,45]

# ---------------------------------------------------------------------------
# Beatty standard DUT                                    [dxf:41], [guide], [ds]
# ---------------------------------------------------------------------------
BEATTY_W_STEP = 51.9 * MIL                # [dxf:41] = 3 x 17.3 mil; silkscreen "Width=3x"; [guide] p. 10 "3x trace width"
BEATTY_L_STEP = 0.787 * INCH              # [dxf:41] 19.99 mm; silkscreen and [guide] "2 cm"
BEATTY_SECTIONS = (                       # [dxf:41] wide section centred on the board
    (20.0 * MM, W_TRACE_50),
    (20.0 * MM, BEATTY_W_STEP),
    (20.0 * MM, W_TRACE_50),
)
BEATTY_Z_NOMINAL = (50.0, 25.0, 50.0)     # ohm [ds] board type 5
BEATTY_Z_STEP_TDR_GUIDE = 22.348          # ohm [guide] fig. 4 marker at 480 ps (measured, rise-time limited)
BEATTY_AFTER_3CM_DEEMBED = (5.0 * MM, 20.0 * MM, 5.0 * MM)   # [guide] p. 9-10: the 3 cm 2x-thru
                                                              # removes 15 mm per side
BEATTY_TRANSITION = "abrupt"              # [guide] p. 10: step made as sharp as possible

# Measured TDR levels read from the guide's marker boxes, for sanity checks only
TDR_GUIDE_FIX_B_50_OHM = 46.919           # ohm [guide] fig. 4, 6 cm fixture B at 490 ps
TDR_GUIDE_FIX_A_105_OHM = 44.875          # ohm [guide] fig. 4, "105% Z0" fixture A at 490 ps

# ---------------------------------------------------------------------------
# "105% Z0" fixture
# ---------------------------------------------------------------------------
Z105_NOMINAL_Z = 45.0    # ohm [guide] p. 8-9 de-embedding cases 5 and 6 call this the "45 Ohm 2xthru";
                         # fig. 4 marker reads 44.875 ohm. FLAG: the board name says "105% Z0" but the
                         # geometry (19 mil vs 17.3 mil, wider = lower Z) and the guide's own numbers
                         # say about 45 ohm, i.e. 90 % of 50 ohm. Treat "105%" as a label, not a ratio.

# ---------------------------------------------------------------------------
# Connectors and adapters                                      [ds], [guide]
# ---------------------------------------------------------------------------
CONNECTOR_SERIES_MM = (2.92, 2.40, 1.85)          # [ds], [guide] edge-launch, 18 per full kit
KIT_BANDWIDTH_GHZ = {2.92: 40, 2.40: 50, 1.85: 70}  # [ds] ordering code, by connector series
ADAPTER_KINDS = ("M/F", "M/M")                    # [guide] p. 5: two phase-matched pairs of each
FLUSH_SHORT = True                                # [guide] p. 5, [ds]: one male flush short per kit

# ---------------------------------------------------------------------------
# Coupon list                                          [ds], [guide], [dxf:all]
# ---------------------------------------------------------------------------
BOARD_TYPES = {                                   # [ds] "five board types"
    1: "6 cm DUT microstrip",
    2: "6 cm test fixture (sides A and B)",
    3: "6 cm 105% Z0 test fixture (sides A and B)",
    4: "2 vias test fixture (sides A and B)",
    5: "Beatty standard DUT",
}
# The ninth board, the 3 cm 2x-thru, is a half-length variant of type 1/2 that
# the guide lists separately as the connector de-embedding 2x-thru.  [guide] p. 5

# Keys are the identifiers used throughout kit370. Fields:
#   part        vendor part number     [dxf:NN] silkscreen and FAB layer; [ds] photos agree
#   dxf         vendor DXF file name   (reference-only, not in this repo)
#   board_type  BOARD_TYPES key, or None for the 3 cm 2x-thru
#   side        "A" / "B" for fixtures, None for DUTs
#   length      board length = trace length, edge to edge
#   w           full trace width
#   connectors  reference designators  [dxf:NN] silkscreen
COUPONS = {
    "DUT_MS":     dict(part="907-000-10140", dxf="6cm_DUT_Microstrip_A-10140.dxf",     board_type=1, side=None,
                       length=BOARD_LENGTH_6CM, w=W_TRACE_50,  connectors=("J1", "J2")),
    "DUT_BEATTY": dict(part="907-000-10141", dxf="Beatty_Standard_DUT-10141.dxf",       board_type=5, side=None,
                       length=BOARD_LENGTH_6CM, w=W_TRACE_50,  connectors=("J3", "J4")),
    "FIX_A":      dict(part="907-000-10142", dxf="6cm_Test_Fixture_A-10142.dxf",        board_type=2, side="A",
                       length=BOARD_LENGTH_6CM, w=W_TRACE_50,  connectors=("J5", "J6")),
    "FIX_B":      dict(part="907-000-10143", dxf="6cm_Test_Fixture_B-10143.dxf",        board_type=2, side="B",
                       length=BOARD_LENGTH_6CM, w=W_TRACE_50,  connectors=("J7", "J8")),
    "VIA_A":      dict(part="907-000-10144", dxf="2_Vias_Test_Fixture_A-10144.dxf",     board_type=4, side="A",
                       length=BOARD_LENGTH_6CM, w=W_TRACE_50,  connectors=("J9", "J10")),
    "VIA_B":      dict(part="907-000-10145", dxf="2_Vias_Test_Fixture_B-10145.dxf",     board_type=4, side="B",
                       length=BOARD_LENGTH_6CM, w=W_TRACE_50,  connectors=("J11", "J12")),
    "Z105_A":     dict(part="907-000-10146", dxf="6cm_105_Z0_Test_Fixture_A-10146.dxf", board_type=3, side="A",
                       length=BOARD_LENGTH_6CM, w=W_TRACE_105, connectors=("J13", "J14")),
    "Z105_B":     dict(part="907-000-10147", dxf="6cm_105_Z0_Test_Fixture_B-10147.dxf", board_type=3, side="B",
                       length=BOARD_LENGTH_6CM, w=W_TRACE_105, connectors=("J15", "J16")),
    "THRU_3CM":   dict(part="907-000-10148", dxf="3cm_2x_Thru-10148.dxf",               board_type=None, side=None,
                       length=BOARD_LENGTH_3CM, w=W_TRACE_50,  connectors=("J17", "J18")),
}

# Layout observations that matter for the examples
FIXTURE_AB_IDENTICAL_IN_DXF = True   # [dxf:42/43, 44/45, 46/47] A and B differ only in silkscreen text.
                                     # Any A/B asymmetry in measured data comes from fabrication and
                                     # connectors, not from layout.
DUT_MS_IDENTICAL_TO_FIX_IN_DXF = True  # [dxf:40 vs 42,43] the 6 cm DUT and the 6 cm fixtures share one layout.
THRU_3CM_HALF_LENGTH = 15.0 * MM     # [guide] p. 9: connector reference plane lands 1.5 cm in from the connector

# ---------------------------------------------------------------------------
# Measurement set M1-M19 and de-embedding computations E1-E8   [guide] p. 6-9
# ---------------------------------------------------------------------------
# Chains are written port 1 -> port 2 in the order the guide lists them.
# Tokens: COUPONS keys; "MF" / "FM" a male-female adapter (orientation as
# listed); "MM" a male-male adapter; "OPEN" / "SHORT" a 1-port termination
# ("SHORT" is the flush short).
MEASUREMENTS = {
    # DUT references
    1:  ("FM", "DUT_MS", "MF"),
    2:  ("FM", "DUT_BEATTY", "MF"),
    # single fixtures
    3:  ("FIX_A", "MF"),
    4:  ("FM", "FIX_B"),
    5:  ("VIA_A", "MF"),
    6:  ("FM", "VIA_B"),
    7:  ("Z105_A", "MF"),
    8:  ("FM", "Z105_B"),
    # 2x-thrus
    9:  ("FIX_A", "MF", "MM", "FIX_B"),
    10: ("VIA_A", "MF", "MM", "VIA_B"),
    11: ("Z105_A", "MF", "MM", "Z105_B"),
    # 1-port open / short on the 50 ohm fixtures
    12: ("FIX_A", "MF", "OPEN"),
    13: ("FIX_A", "MF", "SHORT"),
    14: ("FIX_B", "MF", "OPEN"),
    15: ("FIX_B", "MF", "SHORT"),
    # fixture + DUT + fixture
    16: ("FIX_A", "MM", "FM", "DUT_MS",     "MF", "MM", "FIX_B"),
    17: ("VIA_A", "MM", "FM", "DUT_MS",     "MF", "MM", "VIA_B"),
    18: ("FIX_A", "MM", "FM", "DUT_BEATTY", "MF", "MM", "FIX_B"),
    19: ("VIA_A", "MM", "FM", "DUT_BEATTY", "MF", "MM", "VIA_B"),
}
MEASUREMENT_NPORTS = {m: (1 if m in (12, 13, 14, 15) else 2) for m in MEASUREMENTS}

# Fields: fixtured = M-number of the fixture+DUT measurement; thru = M-number
# of the 2x-thru (or open/short pairs as (side A, side B)); reference = the
# bare-DUT measurement the result is judged against.
DEEMBED_CASES = {
    1: dict(fixtured=16, thru=9,  reference=1, note="50 ohm fixture, 50 ohm 2x-thru"),
    2: dict(fixtured=18, thru=9,  reference=2, note="50 ohm fixture, 50 ohm 2x-thru"),
    3: dict(fixtured=17, thru=10, reference=1, note="2-via fixture, 2-via 2x-thru"),
    4: dict(fixtured=19, thru=10, reference=2, note="2-via fixture, 2-via 2x-thru"),
    5: dict(fixtured=16, thru=11, reference=1, note="50 ohm fixture, 45 ohm 2x-thru: deliberate impedance mismatch"),
    6: dict(fixtured=18, thru=11, reference=2, note="50 ohm fixture, 45 ohm 2x-thru: deliberate impedance mismatch"),
    7: dict(fixtured=16, open=(12, 14), short=(13, 15), reference=1, note="1x-reflect; only if the algorithm supports it"),
    8: dict(fixtured=18, open=(12, 14), short=(13, 15), reference=2, note="1x-reflect; only if the algorithm supports it"),
}

# ---------------------------------------------------------------------------
# Discrepancies between sources - flagged, not resolved
# ---------------------------------------------------------------------------
DISCREPANCIES = (
    "Via drill/pad: guide fig. 3 gives 13 +/-1 mil drill and 23 mil pad; DXF 10144/10145 draw "
    "10 mil drill and 20 mil pad (both signal and ground vias).",
    "Via antipad: guide fig. 3 gives 46 mil on the transmission-line ground and 52 mil on other "
    "grounds; DXF 10144/10145 draw a 30 mil antipad on both L02 and L03.",
    "'105% Z0' fixture: the name implies 52.5 ohm, but the DXF trace is wider (19 vs 17.3 mil), "
    "the guide's cases E5/E6 call it the 45 ohm 2x-thru, and its TDR marker reads 44.9 ohm.",
    "Gold plating: guide states a 75 um minimum, which is physically implausible; 75 uin is likely.",
    "3 cm 2x-thru silkscreen reads 0.984 (in = 25 mm) while its DXF outline is 1.181 in = 30 mm. "
    "The 6 cm boards' silkscreen (2.362) matches their outline.",
    "Dk / Df are not stated in the guide or the datasheet; values here are from Rogers' public "
    "RO4003C and RO4450F pages and must be cited as such.",
    "Datasheet says the nine boards are variations of five types; the 3 cm 2x-thru is a sixth "
    "geometry (half-length type 1/2).",
)
