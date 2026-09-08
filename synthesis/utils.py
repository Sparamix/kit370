#!/usr/bin/env python3
"""
utils.py - geometry and network primitives for kit370 synthesis.

Thin wrappers over scikit-rf. The microstrip physics comes from
``skrf.media.MLine`` and the lumped connector from scikit-rf's lumped
elements. Nothing here re-implements a transmission-line formula.

MLine carries, with citations in its own source (skrf/media/mline.py):
    Hammerstad & Jensen 1980      quasi-static Z0 and er_eff, strip thickness,
                                  current-distribution and roughness factors
    Kirschning & Jansen 1982      dispersion of er_eff and Z0
    Schneider 1969                microstrip dielectric attenuation
    Djordjevic et al. 2001 /
    Svensson & Dermer 2001        causal wideband-Debye dielectric

Holds no material or geometry defaults. Callers pass every physical
parameter explicitly; coupon_specs.py holds the kit's values.

Naming invariants (see CLAUDE.md):
    Z_REF    port / reference impedance for S-parameters and TDR. Always 50 ohm.
    Z0_line  characteristic impedance computed from geometry. Not 50 ohm.

Author: Giorgi Maghlakelidze
License: BSD-3-Clause
"""

import skrf as rf
from skrf.media import MLine, DefinedGammaZ0

# Reference impedance for S-parameters and TDR. Never the line impedance.
Z_REF = 50.0

# Copper resistivity: 100 % IACS is 58.0 MS/m
RHO_CU = 1 / 58.0e6     # ohm*m


# =============================================================================
# Frequency
# =============================================================================

def create_frequency(f_start, f_stop, npoints):
    """
    Linear frequency grid as a scikit-rf Frequency object.

    Parameters
    ----------
    f_start, f_stop : float
        First and last frequency (Hz)
    npoints : int
        Number of points, inclusive of both ends
    """
    return rf.Frequency(start=f_start, stop=f_stop, npoints=npoints, unit='Hz')


# =============================================================================
# Microstrip
# =============================================================================

def microstrip_media(freq, *, w, h, t, er, tand, f_er_tand, roughness=0.0, rho=RHO_CU,
                     dispersion='kirschningjansen', dielectric='djordjevicsvensson'):
    """
    scikit-rf MLine medium for a microstrip on a single dielectric, ports at Z_REF.

    Parameters
    ----------
    freq : rf.Frequency
    w, h, t : float
        Trace width, dielectric height, copper thickness (m)
    er, tand : float
        Relative permittivity and loss tangent, quoted at ``f_er_tand``
    f_er_tand : float
        Frequency (Hz) at which ``er`` and ``tand`` are specified; the
        dielectric model extrapolates them causally across the band
    roughness : float
        RMS conductor roughness (m); 0 disables the correction
    rho : float
        Conductor resistivity (ohm*m)
    dispersion, dielectric : str
        MLine ``disp`` and ``diel`` model names

    Returns
    -------
    skrf.media.MLine
    """
    return MLine(frequency=freq, z0_port=Z_REF, w=w, h=h, t=t, ep_r=er, tand=tand,
                 f_epr_tand=f_er_tand, rough=roughness, rho=rho,
                 model='hammerstadjensen', disp=dispersion, diel=dielectric)


def create_microstrip_network(freq, length_m, *, w, h, t, er, tand, f_er_tand, roughness=0.0,
                              rho=RHO_CU, connector=None, name="microstrip", **media_kw):
    """
    2-port Network for a uniform microstrip line, optionally with a connector
    model cascaded on both ends.

    Parameters
    ----------
    freq : rf.Frequency
    length_m : float
        Physical length (m)
    w, h, t, er, tand, f_er_tand, roughness, rho : float
        See microstrip_media
    connector : rf.Network, optional
        Cascaded on both ends as ``connector ** line ** connector``
    name : str
    **media_kw
        Passed to microstrip_media (``dispersion``, ``dielectric``)

    Returns
    -------
    rf.Network
        With ``.params`` holding the geometry and the computed, frequency-
        dependent ``Z0_line`` and ``er_eff`` arrays
    """
    media = microstrip_media(freq, w=w, h=h, t=t, er=er, tand=tand, f_er_tand=f_er_tand,
                             roughness=roughness, rho=rho, **media_kw)

    ntwk = media.line(length_m, unit='m')
    ntwk.name = name

    ntwk.params = {
        'length_m': length_m,
        'Z0_line': media.z0,            # per frequency, complex
        'er_eff': media.ep_reff_f,      # per frequency, complex
        'w': w, 'h': h, 't': t,
        'er': er, 'tand': tand, 'f_er_tand': f_er_tand,
        'roughness': roughness, 'rho': rho,
    }

    if connector is not None:
        params = ntwk.params  # ** returns a new Network and drops custom attributes
        ntwk = connector ** ntwk ** connector
        ntwk.name = name
        ntwk.params = params

    return ntwk


# =============================================================================
# Connector
# =============================================================================

def create_connector_model(freq, L=100e-12, C=50e-15, name="connector"):
    """
    Lumped connector launch: series L followed by shunt C, referenced to Z_REF.

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
    lumped = DefinedGammaZ0(frequency=freq, z0=Z_REF)
    ntwk = lumped.inductor(L) ** lumped.shunt_capacitor(C)
    ntwk.name = name
    return ntwk
