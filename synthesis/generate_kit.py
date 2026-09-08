#!/usr/bin/env python3
"""
generate_kit.py - kit370 S-parameter Synthesis

Generates virtual P370 kit S-parameter files using scikit-rf.

Author: Giorgi Maghlakelidze
License: BSD-3-Clause
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from utils import create_frequency, create_microstrip_network, create_connector_model

# =============================================================================
# Configuration
# =============================================================================

# Output directory
OUTPUT_DIR = Path("../kit370")

# Frequency setup
F_START = 10e6      # 10 MHz
F_STOP = 67e9       # 67 GHz
F_POINTS = 6701     # ~10 MHz steps

# Material: Rogers RO4350B-euqivalent
DK = 3.48           # Dielectric constant
DF = 0.0037         # Loss tangent (dissipation factor)
F_DK_REF = 10e9     # Frequency at which DK and DF are quoted (Hz)

# Geometry (microstrip on 10 mil dielectric)
H_DIELECTRIC = 0.254e-3     # 10 mil in meters
W_TRACE = 0.559e-3          # ~22 mil for 50 ohm on RO4350B
T_COPPER = 35e-6            # 1 oz copper (35 um)
RMS_ROUGHNESS = 0.5e-6      # 0.5 um RMS surface roughness

# =============================================================================
# Quality checks (scikit-rf; SQualCheck gates come later)
# =============================================================================

def quality_report(ntwk):
    """
    Print passivity and reciprocity from scikit-rf's Network tests.

    Returns True when both pass.
    """
    passive = ntwk.is_passive()
    reciprocal = ntwk.is_reciprocal()
    p_max = np.abs(ntwk.passivity).max()      # sqrt(S^H S) entries, <= 1 when passive
    r_max = ntwk.reciprocity.max().real       # |S - S^T| (skrf stores it in a complex array)

    print(f"\n{ntwk.name}")
    print(f"  Passivity   (Network.is_passive):    {'PASS' if passive else 'FAIL'}   max sqrt(S^H S) = {p_max:.6f}")
    print(f"  Reciprocity (Network.is_reciprocal): {'PASS' if reciprocal else 'FAIL'}   max |S - S^T| = {r_max:.1e}")
    return passive and reciprocal


# =============================================================================
# Plotting Functions
# =============================================================================
# =============================================================================

def plot_tdr(ntwk, ax, color='blue', label=None, kaiser_beta=6):
    """
    Step-response TDR impedance via scikit-rf.

    S11 is extrapolated to DC, then ``Network.plot_z_time_step`` windows,
    pads, integrates to the step response and converts to impedance at the
    port reference. ``pad = N`` gives scikit-rf's ``2(N + pad) - 1`` points,
    i.e. the 4x zero padding convention.
    """
    s11 = ntwk.s11.extrapolate_to_dc(kind='linear')
    s11.plot_z_time_step(m=0, n=0, ax=ax, window=('kaiser', kaiser_beta), pad=len(s11.f),
                         color=color, label=label or ntwk.name)


def create_comparison_plot(networks, colors, output_path=None):
    """
    Create comparison plot with S11, S21, and TDR for multiple networks.
    
    Parameters
    ----------
    networks : list of rf.Network
        Networks to compare
    colors : list of str
        Colors for each network
    output_path : Path, optional
        If provided, save figure to this path
    """
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    fig.suptitle('kit370 - Microstrip Comparison', fontsize=14, fontweight='bold')
    
    ax_s11_mag = axes[0, 0]
    ax_s11_phase = axes[1, 0]
    ax_s21_mag = axes[0, 1]
    ax_s21_phase = axes[1, 1]
    ax_tdr = axes[2, 0]
    ax_info = axes[2, 1]
    
    # Plot each network. scikit-rf plots in the Frequency object's unit, so
    # plot from copies switched to GHz; the originals keep Hz for file output.
    for ntwk, color in zip(networks, colors):
        n_ghz = ntwk.copy()
        n_ghz.frequency.unit = 'GHz'
        n_ghz.plot_s_db(m=0, n=0, ax=ax_s11_mag, color=color, label=ntwk.name)
        n_ghz.plot_s_deg_unwrap(m=0, n=0, ax=ax_s11_phase, color=color, label=ntwk.name, linestyle='--')
        n_ghz.plot_s_db(m=1, n=0, ax=ax_s21_mag, color=color, label=ntwk.name)
        n_ghz.plot_s_deg_unwrap(m=1, n=0, ax=ax_s21_phase, color=color, label=ntwk.name, linestyle='--')
        plot_tdr(ntwk, ax_tdr, color=color, label=ntwk.name)
    
    # Format S11 magnitude
    ax_s11_mag.set_xlabel('Frequency (GHz)')
    ax_s11_mag.set_ylabel('S11 (dB)')
    ax_s11_mag.set_title('S11 Magnitude (Return Loss)')
    ax_s11_mag.legend()
    ax_s11_mag.grid(True, alpha=0.3)
    ax_s11_mag.set_xlim([0, F_STOP])   # scikit-rf plots in Hz and scales the tick labels
    ax_s11_mag.set_ylim([-40, 0])
    
    # Format S11 phase
    ax_s11_phase.set_xlabel('Frequency (GHz)')
    ax_s11_phase.set_ylabel('Phase (degrees)')
    ax_s11_phase.set_title('S11 Unwrapped Phase')
    ax_s11_phase.legend()
    ax_s11_phase.grid(True, alpha=0.3)
    ax_s11_phase.set_xlim([0, F_STOP])   # scikit-rf plots in Hz and scales the tick labels
    
    # Format S21 magnitude
    ax_s21_mag.set_xlabel('Frequency (GHz)')
    ax_s21_mag.set_ylabel('S21 (dB)')
    ax_s21_mag.set_title('S21 Magnitude (Insertion Loss)')
    ax_s21_mag.legend()
    ax_s21_mag.grid(True, alpha=0.3)
    ax_s21_mag.set_xlim([0, F_STOP])   # scikit-rf plots in Hz and scales the tick labels
    ax_s21_mag.set_ylim([-6, 0])
    
    # Format S21 phase
    ax_s21_phase.set_xlabel('Frequency (GHz)')
    ax_s21_phase.set_ylabel('Phase (degrees)')
    ax_s21_phase.set_title('S21 Unwrapped Phase')
    ax_s21_phase.legend()
    ax_s21_phase.grid(True, alpha=0.3)
    ax_s21_phase.set_xlim([0, F_STOP])   # scikit-rf plots in Hz and scales the tick labels
    
    # Format TDR
    ax_tdr.set_xlabel('Time (ns)')
    ax_tdr.set_ylabel('Impedance (Ω)')
    ax_tdr.set_title('TDR Impedance Profile')
    ax_tdr.legend()
    ax_tdr.grid(True, alpha=0.3)
    ax_tdr.set_xlim([-1, 1])
    ax_tdr.set_ylim([40, 60])
    ax_tdr.axhline(y=50, color='gray', linestyle='--', alpha=0.7, label='50Ω ref')
    
    # Info panel
    ax_info.axis('off')
    info_text = "Specifications:\n"
    info_text += f"  Material: RO4350B (Dk={DK}, Df={DF})\n"
    info_text += f"  Dielectric height: {H_DIELECTRIC*1e3:.2f} mm ({H_DIELECTRIC/0.0254*1000:.1f} mil)\n"
    info_text += f"  Trace width: {W_TRACE*1e3:.3f} mm ({W_TRACE/0.0254*1000:.1f} mil)\n"
    info_text += f"  Copper: {T_COPPER*1e6:.0f} µm (1 oz)\n"
    info_text += f"  Surface roughness: {RMS_ROUGHNESS*1e6:.1f} µm RMS\n"
    info_text += f"\nFrequency: {F_START/1e6:.0f} MHz - {F_STOP/1e9:.0f} GHz\n"
    info_text += f"Points: {F_POINTS}\n"
    
    # Add calculated Z0_line at the Dk reference frequency
    if hasattr(networks[0], 'params'):
        i_ref = int(np.argmin(np.abs(networks[0].f - F_DK_REF)))
        info_text += f"\nZ0_line at {F_DK_REF/1e9:.0f} GHz: {networks[0].params['Z0_line'][i_ref].real:.2f} Ω\n"
        info_text += f"Effective εr at {F_DK_REF/1e9:.0f} GHz: {networks[0].params['er_eff'][i_ref].real:.3f}"
    
    ax_info.text(0.1, 0.9, info_text, transform=ax_info.transAxes,
                 fontsize=10, verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot: {output_path}")
    
    return fig


# =============================================================================
# Main Kit Generation
# =============================================================================

def generate_microstrip_duts():
    """Generate the microstrip DUT files."""
    
    print("="*60)
    print("kit370 - Generating Microstrip DUTs")
    print("="*60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Create frequency
    freq = create_frequency(F_START, F_STOP, F_POINTS)
    print(f"\nFrequency: {freq.start/1e6:.0f} MHz - {freq.stop/1e9:.0f} GHz, {freq.npoints} points")

    # Lumped connector launch, cascaded on both ends of each line
    conn = create_connector_model(freq, L=100e-12, C=50e-15)
    
    # Generate 6cm microstrip
    print("\nGenerating 6cm microstrip...")
    ms_6cm = create_microstrip_network(
        freq, 
        length_m=0.06,  # 6 cm
        w=W_TRACE, h=H_DIELECTRIC, t=T_COPPER,
        er=DK, tand=DF, f_er_tand=F_DK_REF, roughness=RMS_ROUGHNESS,
        connector=conn,
        name="dut_microstrip_6cm"
    )
    
    # Generate 3cm microstrip
    print("Generating 3cm microstrip...")
    ms_3cm = create_microstrip_network(
        freq,
        length_m=0.03,  # 3 cm
        w=W_TRACE, h=H_DIELECTRIC, t=T_COPPER,
        er=DK, tand=DF, f_er_tand=F_DK_REF, roughness=RMS_ROUGHNESS,
        connector=conn,
        name="dut_microstrip_3cm"
    )
    
    # Print calculated parameters
    i_ref = int(np.argmin(np.abs(freq.f - F_DK_REF)))
    print(f"\nMicrostrip parameters at {freq.f[i_ref]/1e9:.0f} GHz:")
    print(f"  Characteristic impedance: {ms_6cm.params['Z0_line'][i_ref].real:.2f} Ω")
    print(f"  Effective permittivity: {ms_6cm.params['er_eff'][i_ref].real:.3f}")
    
    # Quality check
    print("\n--- Quality Checks ---")
    quality_report(ms_6cm)
    quality_report(ms_3cm)
    
    # Save touchstone files
    ts_6cm = OUTPUT_DIR / "dut_microstrip_6cm.s2p"
    ts_3cm = OUTPUT_DIR / "dut_microstrip_3cm.s2p"
    
    ms_6cm.write_touchstone(ts_6cm)
    print(f"Saved: {ts_6cm}")
    
    ms_3cm.write_touchstone(ts_3cm)
    print(f"Saved: {ts_3cm}")
    
    # Create comparison plot
    print("\nGenerating comparison plot...")
    plot_path = OUTPUT_DIR / "microstrip_comparison.png"
    create_comparison_plot(
        networks=[ms_6cm, ms_3cm],
        colors=['blue', 'red'],
        output_path=plot_path
    )
    
    print("\n" + "="*60)
    print("Generation complete!")
    print("="*60)
    
    return ms_6cm, ms_3cm


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    generate_microstrip_duts()
    plt.show()
