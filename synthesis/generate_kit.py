#!/usr/bin/env python3
"""
generate_kit.py - openSNPKit370 S-parameter Synthesis

Generates virtual P370 kit S-parameter files using scikit-rf.

Author: Giorgi Maghlakelidze
License: BSD-3-Clause
"""

import numpy as np
import skrf as rf
import matplotlib.pyplot as plt
from pathlib import Path

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

# Geometry (microstrip on 10 mil dielectric)
H_DIELECTRIC = 0.254e-3     # 10 mil in meters
W_TRACE = 0.559e-3          # ~22 mil for 50 ohm on RO4350B
T_COPPER = 35e-6            # 1 oz copper (35 um)
RMS_ROUGHNESS = 0.5e-6      # 0.5 um RMS surface roughness

# Reference impedance
Z0 = 50

# =============================================================================
# Helper Functions
# =============================================================================

def create_frequency(f_start=F_START, f_stop=F_STOP, npoints=F_POINTS):
    """Create scikit-rf Frequency object."""
    return rf.Frequency(start=f_start, stop=f_stop, npoints=npoints, unit='Hz')


def calc_microstrip_params(freq_hz, w, h, t, er, tand, roughness=0):
    """
    Calculate microstrip characteristic impedance and propagation constant.
    
    Uses Wheeler's equations for Z0 and effective permittivity,
    plus conductor and dielectric loss models.
    
    Parameters
    ----------
    freq_hz : array
        Frequency in Hz
    w : float
        Trace width (m)
    h : float
        Dielectric height (m)
    t : float
        Copper thickness (m)
    er : float
        Relative permittivity (Dk)
    tand : float
        Loss tangent (Df)
    roughness : float
        RMS surface roughness (m)
    
    Returns
    -------
    Z0 : float
        Characteristic impedance (ohms)
    gamma : array
        Complex propagation constant (1/m)
    """
    # Physical constants
    c0 = 299792458.0        # Speed of light (m/s)
    mu0 = 4 * np.pi * 1e-7  # Permeability of free space
    sigma_cu = 5.8e7        # Copper conductivity (S/m)
    
    # Effective width (accounts for copper thickness)
    if w / h > 1 / (2 * np.pi):
        w_eff = w + (t / np.pi) * (1 + np.log(2 * h / t))
    else:
        w_eff = w + (t / np.pi) * (1 + np.log(4 * np.pi * w / t))
    
    # Effective dielectric constant (Hammerstad-Jensen)
    u = w_eff / h
    a = 1 + (1/49) * np.log((u**4 + (u/52)**2) / (u**4 + 0.432)) + (1/18.7) * np.log(1 + (u/18.1)**3)
    b = 0.564 * ((er - 0.9) / (er + 3))**0.053
    
    er_eff = (er + 1) / 2 + ((er - 1) / 2) * (1 + 10 / u)**(-a * b)
    
    # Characteristic impedance (Wheeler)
    F = 6 + (2 * np.pi - 6) * np.exp(-(30.666 / u)**0.7528)
    Z0_calc = (60 / np.sqrt(er_eff)) * np.log(F / u + np.sqrt(1 + (2 / u)**2))
    
    # Wavenumber
    omega = 2 * np.pi * freq_hz
    k0 = omega / c0
    
    # Phase constant
    beta = k0 * np.sqrt(er_eff)
    
    # Skin depth
    delta_s = np.sqrt(2 / (omega * mu0 * sigma_cu))
    
    # Conductor loss (with surface roughness - Huray model simplified)
    Rs = 1 / (sigma_cu * delta_s)  # Surface resistance
    
    # Roughness correction factor (simplified Huray)
    if roughness > 0:
        K_sr = 1 + (2 / np.pi) * np.arctan(1.4 * (roughness / delta_s)**2)
    else:
        K_sr = 1.0
    
    alpha_c = (Rs * K_sr) / (Z0_calc * w_eff)
    
    # Dielectric loss (Djordjevic-Sarkar simplified)
    alpha_d = (k0 * np.sqrt(er_eff) * tand) / 2
    
    # Total propagation constant
    alpha = alpha_c + alpha_d
    gamma = alpha + 1j * beta
    
    return Z0_calc, gamma, er_eff


def create_microstrip_network(freq, length_m, w=W_TRACE, h=H_DIELECTRIC, 
                               t=T_COPPER, er=DK, tand=DF, roughness=RMS_ROUGHNESS, add_connectors=False,
                               name="microstrip"):
    """
    Create a 2-port Network for a microstrip transmission line.
    
    Parameters
    ----------
    freq : rf.Frequency
        Frequency object
    length_m : float
        Physical length in meters
    w, h, t, er, tand, roughness : float
        Microstrip parameters (see calc_microstrip_params)
    name : str
        Network name
    
    Returns
    -------
    rf.Network
        2-port S-parameter network
    """
    f_hz = freq.f
    npoints = len(f_hz)
    
    # Calculate line parameters
    Z0_line, gamma, er_eff = calc_microstrip_params(
        f_hz, w, h, t, er, tand, roughness
    )
    
    # Build S-parameter matrix from ABCD
    # ABCD for transmission line: [[cosh(γl), Z0*sinh(γl)], [sinh(γl)/Z0, cosh(γl)]]
    gl = gamma * length_m
    
    A = np.cosh(gl)
    B = Z0_line * np.sinh(gl)
    C = np.sinh(gl) / Z0_line
    D = np.cosh(gl)
    
    # Convert ABCD to S-parameters (reference Z0 = 50 ohms)
    Z0_ref = Z0
    
    denom = A + B/Z0_ref + C*Z0_ref + D
    
    S11 = (A + B/Z0_ref - C*Z0_ref - D) / denom
    S12 = 2 * (A*D - B*C) / denom
    S21 = 2 / denom
    S22 = (-A + B/Z0_ref - C*Z0_ref + D) / denom
    
    # Build S-matrix
    s = np.zeros((npoints, 2, 2), dtype=complex)
    s[:, 0, 0] = S11
    s[:, 0, 1] = S12
    s[:, 1, 0] = S21
    s[:, 1, 1] = S22
    
    # Create network
    ntwk = rf.Network(frequency=freq, s=s, z0=Z0_ref, name=name)
    
    # Store metadata
    ntwk.params = {
        'length_m': length_m,
        'Z0_line': Z0_line,
        'er_eff': er_eff,
        'w': w,
        'h': h,
        'er': er,
        'tand': tand
    }
    
    if add_connectors:
        params = ntwk.params  # Save before cascade
        conn = create_connector_model(freq, L=100e-12, C=50e-15)
        ntwk = conn ** ntwk ** conn
        ntwk.name = name
        ntwk.params = params
        
    return ntwk

def create_connector_model(freq, L=100e-12, C=50e-15, name="connector"):
    """
    Create a simple connector model (series L + shunt C).
    
    Parameters
    ----------
    freq : rf.Frequency
    L : float
        Series inductance (H), default 100 pH
    C : float
        Shunt capacitance (F), default 50 fF
    name : str
    
    Returns
    -------
    rf.Network
    """
    omega = 2 * np.pi * freq.f
    npoints = len(freq.f)
    
    # Series inductor: Z = jωL
    Z_L = 1j * omega * L
    
    # Shunt capacitor: Y = jωC
    Y_C = 1j * omega * C
    
    # ABCD of series Z: [[1, Z], [0, 1]]
    # ABCD of shunt Y: [[1, 0], [Y, 1]]
    # Combined: series L then shunt C
    A = 1 + Z_L * Y_C
    B = Z_L
    C_abcd = Y_C
    D = np.ones(npoints)
    
    # Convert ABCD to S
    Z0_ref = Z0
    denom = A + B/Z0_ref + C_abcd*Z0_ref + D
    
    S11 = (A + B/Z0_ref - C_abcd*Z0_ref - D) / denom
    S12 = 2 * (A*D - B*C_abcd) / denom
    S21 = 2 / denom
    S22 = (-A + B/Z0_ref - C_abcd*Z0_ref + D) / denom
    
    s = np.zeros((npoints, 2, 2), dtype=complex)
    s[:, 0, 0] = S11
    s[:, 0, 1] = S12
    s[:, 1, 0] = S21
    s[:, 1, 1] = S22
    
    return rf.Network(frequency=freq, s=s, z0=Z0_ref, name=name)

# =============================================================================
# Quality Metrics (Placeholder - will integrate openSNPQual later)
# =============================================================================

def calculate_quality_metrics(ntwk):
    """
    Calculate S-parameter quality metrics.
    
    PLACEHOLDER: Will be replaced with openSNPQual integration.
    
    Parameters
    ----------
    ntwk : rf.Network
        Network to analyze
    
    Returns
    -------
    dict
        Quality metrics
    """
    metrics = {
        'name': ntwk.name,
        'passivity': {},
        'reciprocity': {},
        'causality': {}
    }
    
    # --- Passivity (frequency domain) ---
    # Check if max singular value <= 1
    s = ntwk.s
    max_sv = 0
    for i in range(len(ntwk.f)):
        sv = np.linalg.svd(s[i], compute_uv=False)
        max_sv = max(max_sv, np.max(sv))
    
    metrics['passivity']['max_singular_value'] = max_sv
    metrics['passivity']['pass'] = max_sv <= 1.001  # Small tolerance for numerical error
    
    # --- Reciprocity (S12 == S21 for passive 2-port) ---
    if ntwk.nports == 2:
        s12 = ntwk.s[:, 0, 1]
        s21 = ntwk.s[:, 1, 0]
        recip_error = np.max(np.abs(s12 - s21))
        recip_error_db = 20 * np.log10(recip_error + 1e-15)
        
        metrics['reciprocity']['max_error'] = recip_error
        metrics['reciprocity']['max_error_dB'] = recip_error_db
        metrics['reciprocity']['pass'] = recip_error_db < -40
    
    # --- Causality (placeholder - simplified check) ---
    # TODO: Proper Hilbert transform / Kramers-Kronig check
    # For now, just flag as "not checked"
    metrics['causality']['checked'] = False
    metrics['causality']['note'] = "Placeholder - integrate openSNPQual"
    
    return metrics


def print_quality_report(metrics):
    """Print quality metrics in readable format."""
    print(f"\n{'='*60}")
    print(f"Quality Report: {metrics['name']}")
    print(f"{'='*60}")
    
    # Passivity
    p = metrics['passivity']
    status = "✓ PASS" if p['pass'] else "✗ FAIL"
    print(f"Passivity:   Max SV = {p['max_singular_value']:.6f}  {status}")
    
    # Reciprocity
    if 'max_error_dB' in metrics['reciprocity']:
        r = metrics['reciprocity']
        status = "✓ PASS" if r['pass'] else "✗ FAIL"
        print(f"Reciprocity: Error = {r['max_error_dB']:.1f} dB  {status}")
    
    # Causality
    c = metrics['causality']
    if c['checked']:
        status = "✓ PASS" if c['pass'] else "✗ FAIL"
        print(f"Causality:   {status}")
    else:
        print(f"Causality:   {c['note']}")
    
    print(f"{'='*60}\n")


# =============================================================================
# Plotting Functions
# =============================================================================

def plot_s11(ntwk, ax_mag, ax_phase, color='blue', label=None):
    """Plot S11 magnitude and unwrapped phase."""
    f_ghz = ntwk.f / 1e9
    s11_db = 20 * np.log10(np.abs(ntwk.s[:, 0, 0]) + 1e-15)
    s11_phase = np.unwrap(np.angle(ntwk.s[:, 0, 0])) * 180 / np.pi
    
    lbl = label or ntwk.name
    ax_mag.plot(f_ghz, s11_db, color=color, label=lbl)
    ax_phase.plot(f_ghz, s11_phase, color=color, label=lbl, linestyle='--')


def plot_s21(ntwk, ax_mag, ax_phase, color='blue', label=None):
    """Plot S21 magnitude and unwrapped phase."""
    f_ghz = ntwk.f / 1e9
    s21_db = 20 * np.log10(np.abs(ntwk.s[:, 1, 0]) + 1e-15)
    s21_phase = np.unwrap(np.angle(ntwk.s[:, 1, 0])) * 180 / np.pi
    
    lbl = label or ntwk.name
    ax_mag.plot(f_ghz, s21_db, color=color, label=lbl)
    ax_phase.plot(f_ghz, s21_phase, color=color, label=lbl, linestyle='--')


def plot_tdr(ntwk, ax, color='blue', label=None, kaiser_beta=6):
    """
    Plot TDR impedance profile with Kaiser windowing.
    
    Parameters
    ----------
    ntwk : rf.Network
        Network to analyze
    ax : matplotlib axis
        Axis to plot on
    color : str
        Line color
    label : str
        Legend label
    kaiser_beta : float
        Kaiser window beta parameter (0=rectangular, 5=similar to Hamming, 
        6=similar to Hanning, 8.6=similar to Blackman)
    """
    lbl = label or ntwk.name
    
    # Get S11 data
    s11 = ntwk.s[:, 0, 0]
    npoints = len(s11)
    
    # Apply Kaiser window
    window = np.kaiser(npoints, kaiser_beta)
    s11_windowed = s11 * window
    
    # Zero-pad for better time resolution (4x)
    nfft = npoints * 4
    
    # Compute IFFT (shift to center zero-time)
    s11_td = np.fft.ifft(s11_windowed, n=nfft)
    s11_td = np.fft.fftshift(s11_td)
    
    # Time axis
    df = ntwk.f[1] - ntwk.f[0]  # Frequency step
    t_total = 1 / df  # Total time span
    t = np.linspace(-t_total/2, t_total/2, nfft) * 1e9  # Convert to ns
    
    # Calculate impedance from reflection coefficient
    # Z = Z0 * (1 + Gamma) / (1 - Gamma)
    gamma_t = s11_td
    
    # Avoid division by zero
    denom = 1 - gamma_t
    denom = np.where(np.abs(denom) < 1e-10, 1e-10, denom)
    z_t = Z0 * np.real((1 + gamma_t) / denom)
    
    # Clip to reasonable range
    z_t = np.clip(z_t, 0, 150)
    
    ax.plot(t, z_t, color=color, label=lbl)


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
    fig.suptitle('openSNPKit370 - Microstrip Comparison', fontsize=14, fontweight='bold')
    
    ax_s11_mag = axes[0, 0]
    ax_s11_phase = axes[1, 0]
    ax_s21_mag = axes[0, 1]
    ax_s21_phase = axes[1, 1]
    ax_tdr = axes[2, 0]
    ax_info = axes[2, 1]
    
    # Plot each network
    for ntwk, color in zip(networks, colors):
        plot_s11(ntwk, ax_s11_mag, ax_s11_phase, color=color, label=ntwk.name)
        plot_s21(ntwk, ax_s21_mag, ax_s21_phase, color=color, label=ntwk.name)
        plot_tdr(ntwk, ax_tdr, color=color, label=ntwk.name)
    
    # Format S11 magnitude
    ax_s11_mag.set_xlabel('Frequency (GHz)')
    ax_s11_mag.set_ylabel('S11 (dB)')
    ax_s11_mag.set_title('S11 Magnitude (Return Loss)')
    ax_s11_mag.legend()
    ax_s11_mag.grid(True, alpha=0.3)
    ax_s11_mag.set_xlim([0, 67])
    ax_s11_mag.set_ylim([-40, 0])
    
    # Format S11 phase
    ax_s11_phase.set_xlabel('Frequency (GHz)')
    ax_s11_phase.set_ylabel('Phase (degrees)')
    ax_s11_phase.set_title('S11 Unwrapped Phase')
    ax_s11_phase.legend()
    ax_s11_phase.grid(True, alpha=0.3)
    ax_s11_phase.set_xlim([0, 67])
    
    # Format S21 magnitude
    ax_s21_mag.set_xlabel('Frequency (GHz)')
    ax_s21_mag.set_ylabel('S21 (dB)')
    ax_s21_mag.set_title('S21 Magnitude (Insertion Loss)')
    ax_s21_mag.legend()
    ax_s21_mag.grid(True, alpha=0.3)
    ax_s21_mag.set_xlim([0, 67])
    ax_s21_mag.set_ylim([-6, 0])
    
    # Format S21 phase
    ax_s21_phase.set_xlabel('Frequency (GHz)')
    ax_s21_phase.set_ylabel('Phase (degrees)')
    ax_s21_phase.set_title('S21 Unwrapped Phase')
    ax_s21_phase.legend()
    ax_s21_phase.grid(True, alpha=0.3)
    ax_s21_phase.set_xlim([0, 67])
    
    # Format TDR
    ax_tdr.set_xlabel('Time (ns)')
    ax_tdr.set_ylabel('Impedance (Ω)')
    ax_tdr.set_title('TDR Impedance Profile')
    ax_tdr.legend()
    ax_tdr.grid(True, alpha=0.3)
    ax_tdr.set_xlim([-1, 1])
    ax_tdr.set_ylim([45, 55])
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
    
    # Add calculated Z0
    if hasattr(networks[0], 'params'):
        info_text += f"\nCalculated Z0: {networks[0].params['Z0_line']:.2f} Ω\n"
        info_text += f"Effective εr: {networks[0].params['er_eff']:.3f}"
    
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
    print("openSNPKit370 - Generating Microstrip DUTs")
    print("="*60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Create frequency
    freq = create_frequency()
    print(f"\nFrequency: {freq.start/1e6:.0f} MHz - {freq.stop/1e9:.0f} GHz, {freq.npoints} points")
    
    # Generate 6cm microstrip
    print("\nGenerating 6cm microstrip...")
    ms_6cm = create_microstrip_network(
        freq, 
        length_m=0.06,  # 6 cm
        add_connectors=True,
        name="dut_microstrip_6cm"
    )
    
    # Generate 3cm microstrip
    print("Generating 3cm microstrip...")
    ms_3cm = create_microstrip_network(
        freq,
        length_m=0.03,  # 3 cm
        add_connectors=True,
        name="dut_microstrip_3cm"
    )
    
    # Print calculated parameters
    print(f"\nMicrostrip parameters:")
    print(f"  Characteristic impedance: {ms_6cm.params['Z0_line']:.2f} Ω")
    print(f"  Effective permittivity: {ms_6cm.params['er_eff']:.3f}")
    
    # Quality check
    print("\n--- Quality Checks ---")
    metrics_6cm = calculate_quality_metrics(ms_6cm)
    print_quality_report(metrics_6cm)
    
    metrics_3cm = calculate_quality_metrics(ms_3cm)
    print_quality_report(metrics_3cm)
    
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
