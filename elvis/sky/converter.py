"""
Convert the sky section of an ETC JSON file to skycalc_ipy parameters.

Produces either a parameter dict suitable for ``SkyCalc.update()`` or a
YAML string that can be passed to ``SkyCalc(ipt_str=...)``.

Parameter mapping
-----------------
ETC JSON (Format A / B)    →  skycalc_ipy
``sky.airmass``            →  ``airmass``
``sky.waterVapour / pwv``  →  ``pwv``       (with ``pwv_mode='pwv'``)
``sky.moonDistance``        →  ``moon_target_sep``
``sky.fli / moon_fli``     →  ``moon_sun_sep``  (via FLI → phase angle)
                              ``moon_alt``       (estimated from FLI)

The Fractional Lunar Illumination (FLI) is converted to a Moon–Sun
separation angle using the approximate relation:

    FLI ≈ (1 − cos(moon_sun_sep)) / 2

Moon altitude is estimated from FLI: full moon is assumed overhead
(``+45°``), new moon below horizon (``-90°``), linearly interpolated.
"""

from __future__ import annotations

import math

import yaml


# Valid PWV steps accepted by skycalc microservice (nearest is chosen)
_PWV_STEPS = [-1.0, 0.5, 1.0, 1.5, 2.5, 3.5, 5.0, 7.5, 10.0, 20.0]


def _fli_to_moon_sun_sep(fli: float) -> float:
    """Convert Fractional Lunar Illumination to Moon–Sun separation [deg].

    Uses FLI ≈ (1 − cos(sep)) / 2  →  sep = arccos(1 − 2·FLI).
    """
    fli = max(0.0, min(1.0, fli))
    return math.degrees(math.acos(1.0 - 2.0 * fli))


def _fli_to_moon_alt(fli: float) -> float:
    """Estimate moon altitude from FLI.

    When the moon is visible (FLI > 0.05), we assume a reasonable
    altitude that increases with illumination.  For effectively new
    moon (FLI ≤ 0.05) the moon is placed below the horizon and the
    ``incl_moon`` flag should be set to ``'N'``.
    """
    fli = max(0.0, min(1.0, fli))
    if fli <= 0.05:
        return -90.0
    # Scale from 20° (thin crescent) to 45° (full moon)
    return 20.0 + 25.0 * fli


def _nearest_pwv(pwv: float) -> float:
    """Snap to the nearest PWV value accepted by the skycalc service."""
    return min(_PWV_STEPS, key=lambda v: abs(v - pwv))


def etc_sky_to_skycalc(etc_json: dict) -> dict:
    """
    Convert ETC JSON sky parameters to a skycalc_ipy parameter dict.

    Parameters
    ----------
    etc_json : dict
        Full ETC JSON (with ``sky`` key), or just the ``sky`` sub-dict.

    Returns
    -------
    dict
        Keys match ``skycalc_ipy.ui.SkyCalc`` parameter names.
        Can be applied via ``skycalc.update(result)`` or serialised
        with :func:`to_skycalc_yaml`.
    """
    sky = etc_json.get("sky", etc_json)

    # --- Airmass ---
    airmass = float(sky.get("airmass", 1.2))

    # --- PWV (Format A: waterVapour, Format B: pwv) ---
    pwv = float(sky.get("pwv", sky.get("waterVapour", 3.5)))
    pwv = _nearest_pwv(pwv)

    # --- Moon FLI (Format A: fli, Format B: moon_fli) ---
    fli = float(sky.get("fli", sky.get("moon_fli", 0.5)))
    moon_sun_sep = _fli_to_moon_sun_sep(fli)
    incl_moon = "N" if fli <= 0.05 else "Y"

    # --- Moon-target separation ---
    moon_target_sep = float(sky.get("moonDistance",
                                    sky.get("moon_target_sep", 45.0)))

    # --- Moon altitude (must satisfy geometric constraint) ---
    # skycalc requires: |z - zmoon| <= rho <= |z + zmoon|
    # where z = arccos(1/airmass), zmoon = 90 - moon_alt, rho = moon_target_sep
    target_zenith = math.degrees(math.acos(1.0 / max(airmass, 1.0)))
    moon_alt = _fli_to_moon_alt(fli)
    moon_zenith = 90.0 - moon_alt

    # Ensure geometric validity: clamp moon_target_sep to valid range
    rho_min = abs(target_zenith - moon_zenith)
    rho_max = abs(target_zenith + moon_zenith)
    if rho_max > 180.0:
        rho_max = 180.0
    if moon_target_sep < rho_min or moon_target_sep > rho_max:
        moon_target_sep = max(rho_min, min(moon_target_sep, rho_max))

    return {
        "airmass": airmass,
        "pwv_mode": "pwv",
        "pwv": pwv,
        "incl_moon": incl_moon,
        "moon_sun_sep": round(moon_sun_sep, 2),
        "moon_target_sep": round(moon_target_sep, 2),
        "moon_alt": round(moon_alt, 2),
        "moon_earth_dist": 1.0,
        "observatory": "paranal",
    }


def to_skycalc_yaml(params: dict) -> str:
    """
    Serialise a skycalc parameter dict to a YAML string that can be
    passed directly to ``SkyCalc(ipt_str=...)``.

    The output contains the full default parameter set with the
    converted values merged in, so the SkyCalc object is complete.

    Parameters
    ----------
    params : dict
        Output of :func:`etc_sky_to_skycalc`.

    Returns
    -------
    str
        YAML string loadable by ``SkyCalc.__init__``.
    """
    from skycalc_ipy.ui import SkyCalc
    ref = SkyCalc()
    merged = dict(ref.values)
    merged.update(params)

    # Build a YAML string matching params.yaml schema:
    #   key:
    #     - value
    #     - type
    #     - check_type
    #     - allowed
    #     - comment
    out = {}
    for key in merged:
        out[key] = [
            merged[key],
            ref.data_type.get(key, "float"),
            ref.check_type.get(key, "no_check"),
            ref.allowed.get(key, []),
            ref.comments.get(key, ""),
        ]

    return yaml.dump(out, default_flow_style=False, sort_keys=False)


def apply_to_skycalc(etc_json: dict):
    """
    Create a ready-to-use ``SkyCalc`` object from an ETC JSON dict.

    Parameters
    ----------
    etc_json : dict
        Full ETC JSON or just the ``sky`` sub-dict.

    Returns
    -------
    skycalc_ipy.ui.SkyCalc
        Configured SkyCalc instance.
    """
    from skycalc_ipy.ui import SkyCalc
    params = etc_sky_to_skycalc(etc_json)
    skycalc = SkyCalc()
    skycalc.update(params)
    return skycalc
