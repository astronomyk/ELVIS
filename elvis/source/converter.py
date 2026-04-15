"""
Convert an ETC JSON target section to scopesim-targets YAML syntax.

This module provides a function that takes the JSON output of the ESO ETC 2.0,
extracts the target information, and converts it to a dictionary (and
optionally a YAML string) compatible with scopesim-targets.

Supported mappings
------------------
Morphology:
    - point → Star (single point source at origin)
    - extended/sersic → Sersic (with r_eff, n, ellip, theta)
    - extended/infinite → not directly supported by scopesim-targets
      (raises ValueError with guidance)

SED / spectrum:
    - template (MARCS/PHOENIX) → "blackbody:<Teff> K"
    - template (SWIRE) → "blackbody:5000 K" (generic galaxy SED placeholder)
    - blackbody → "blackbody:<T> K"
    - powerlaw → "powerlaw:<exponent>"  (custom extension, not natively
      supported by scopesim-targets; requires special handling downstream)
    - emissionline → not supported (raises ValueError)

Brightness:
    - ETC magband + mag + magsys → brightness tuple ("band", mag)
    - Only standard broadband filters (U..N) are passed through; survey
      filters (SDSS, Gaia, etc.) are mapped to the nearest standard band.
"""

from __future__ import annotations

import yaml
from astropy import units as u


# Survey-band → nearest standard band mapping for scopesim-targets
_BAND_MAP = {
    # Standard bands pass through
    "U": "U", "B": "B", "V": "V", "R": "R", "I": "I",
    "Y": "Y", "J": "J", "H": "H", "K": "K", "L": "L", "M": "M", "N": "N",
    # Gaia
    "gaia_GBP": "B", "gaia_G": "V", "gaia_GRP": "R",
    # SDSS
    "sdss_u": "U", "sdss_g": "V", "sdss_r": "R", "sdss_i": "I", "sdss_z": "I",
    # DECam
    "DECam_g": "V", "DECam_r": "R", "DECam_i": "I", "DECam_z": "I",
    # LSST
    "lsst_u": "U", "lsst_g": "V", "lsst_r": "R",
    "lsst_i": "I", "lsst_z": "I", "lsst_y": "Y",
    # VISTA
    "VISTA_Y": "Y", "VISTA_Z": "I", "VISTA_J": "J",
    "VISTA_H": "H", "VISTA_Ks": "K",
    # 4MOST
    "4MOST_Johnson_B": "B", "4MOST_Johnson_V": "V",
    "4MOST_Cousins_R": "R", "4MOST_Cousins_I": "I",
}


def etc_target_to_scopesim_yaml(etc_json: dict) -> dict:
    """
    Convert an ETC JSON target section to a scopesim-targets YAML dict.

    Parameters
    ----------
    etc_json : dict
        Full ETC JSON dict (containing ``target`` key), or just the
        ``target`` sub-dict itself.

    Returns
    -------
    dict
        A dictionary with keys ``target_class``, ``position``,
        ``spectrum``, ``brightness``, and optionally ``params``
        (for Sersic targets). This dict can be serialised to YAML via
        :func:`to_yaml_string`, or used directly to construct
        scopesim-targets objects via :func:`to_scopesim_target`.

    Raises
    ------
    ValueError
        If the target configuration cannot be mapped to scopesim-targets
        (e.g. infinite extended sources or emission-line SEDs).
    """
    target = etc_json.get("target", etc_json)
    morph = target.get("morphology", {})
    sed = target.get("sed", {})
    bright = target.get("brightness", {})

    result = {"position": [0, 0]}

    # ---- Morphology ----
    morph_type = morph.get("morphologytype", "point")
    if morph_type == "point":
        result["target_class"] = "Star"

    elif morph_type == "extended":
        ext_type = morph.get("extendedtype")
        if ext_type == "sersic":
            result["target_class"] = "Sersic"
            result["params"] = {
                "r_eff": float(morph.get("radius", 0.5)) * u.arcsec,
                "n": float(morph.get("index", 4)),
                "ellip": float(morph.get("ellipticity", 0.0)),
                "theta": float(morph.get("angle", 0.0)) * u.deg,
            }
        elif ext_type == "infinite":
            raise ValueError(
                "Infinite extended sources have no direct scopesim-targets "
                "YAML equivalent. Use a large Sersic with n≈0 or build a "
                "scopesim Source from an ImageHDU directly."
            )
        else:
            raise ValueError(f"Unknown extendedtype: {ext_type}")
    else:
        raise ValueError(f"Unknown morphologytype: {morph_type}")

    # ---- Spectrum / SED ----
    result["spectrum"] = _convert_sed(sed)

    # ---- Brightness ----
    result["brightness"] = _convert_brightness(bright)

    return result


def _convert_sed(sed: dict) -> str:
    """Map the ETC sed section to a scopesim-targets spectrum string."""
    sedtype = sed.get("sedtype", "spectrum")

    if sedtype == "emissionline":
        raise ValueError(
            "Emission-line SEDs are not directly supported by "
            "scopesim-targets YAML syntax."
        )

    spectrum = sed.get("spectrum", {})
    spectype = spectrum.get("spectrumtype", "template")
    params = spectrum.get("params", {})

    if spectype == "template":
        catalog = params.get("catalog", "MARCS")
        sed_id = params.get("id", "5750:4.5")

        if catalog in ("MARCS", "PHOENIX"):
            teff = sed_id.split(":")[0]
            return f"blackbody:{teff} K"

        # SWIRE / other galaxy templates → generic
        return "blackbody:5000 K"

    if spectype == "blackbody":
        temp = params.get("temperature", 5000)
        return f"blackbody:{int(temp)} K"

    if spectype == "powerlaw":
        exponent = params.get("exponent", 0)
        return f"powerlaw:{exponent}"

    if spectype == "upload":
        raise ValueError(
            "Uploaded spectra cannot be converted to YAML. "
            "Pass the spectrum file directly to scopesim."
        )

    raise ValueError(f"Unknown spectrumtype: {spectype}")


def _convert_brightness(bright: dict) -> tuple:
    """Map the ETC brightness section to a (band, mag) tuple."""
    magband = bright.get("magband", "V")
    mag = float(bright.get("mag", 10))

    band = _BAND_MAP.get(magband, "V")
    return (band, mag * u.mag)


# -------------------------------------------------------------------------
#  Serialisation helpers
# -------------------------------------------------------------------------

def to_yaml_string(yaml_dict: dict) -> str:
    """
    Serialise the output of :func:`etc_target_to_scopesim_yaml` to a YAML
    string loadable by scopesim-targets.

    Parameters
    ----------
    yaml_dict : dict
        Output of ``etc_target_to_scopesim_yaml``.

    Returns
    -------
    str
        A YAML-formatted string starting with ``!Star`` or ``!Sersic``.
    """
    tag = yaml_dict["target_class"]
    lines = [f"!{tag}"]
    lines.append(f"position: {list(yaml_dict['position'])}")
    lines.append(f'spectrum: "{yaml_dict["spectrum"]}"')

    band, mag = yaml_dict["brightness"]
    lines.append(f'brightness: ["{band}", {mag.value} mag]')

    if "params" in yaml_dict:
        lines.append("params:")
        p = yaml_dict["params"]
        if "r_eff" in p:
            lines.append(f"  r_eff: {p['r_eff'].value} arcsec")
        if "n" in p:
            lines.append(f"  n: {p['n']}")
        if "ellip" in p:
            lines.append(f"  ellip: {p['ellip']}")
        if "theta" in p:
            lines.append(f"  theta: {p['theta'].value} deg")

    return "\n".join(lines) + "\n"


def to_scopesim_target(yaml_dict: dict):
    """
    Construct a scopesim-targets Target object from the converter output.

    For point sources with blackbody spectra, the spectrum is pre-resolved
    to a ``SourceSpectrum`` because scopesim-targets' ``resolve_spectrum``
    requires brightness to be threaded through for blackbody strings, which
    the Star constructor's internal path does not do.

    Parameters
    ----------
    yaml_dict : dict
        Output of ``etc_target_to_scopesim_yaml``.

    Returns
    -------
    scopesim_targets.target.Target
        A ``Star`` or ``Sersic`` instance ready for ``.to_source()``.
    """
    from scopesim_targets.point_source import Star
    from scopesim_targets.extended_source import Sersic
    from spextra import Spextrum

    cls_name = yaml_dict["target_class"]
    spectrum_str = yaml_dict["spectrum"]
    brightness = yaml_dict["brightness"]

    # For Star + blackbody, pre-resolve to SourceSpectrum so that
    # resolve_spectrum doesn't hit the brightness=None bug.
    if cls_name == "Star" and spectrum_str.startswith("blackbody:"):
        temp = u.Quantity(spectrum_str.removeprefix("blackbody:"))
        band, mag = brightness
        spec = Spextrum.black_body_spectrum(temp, mag, band)
        spectrum = spec
        # Brightness already baked into the spectrum; still pass it
        # so the Star object stores it for metadata.
    else:
        spectrum = spectrum_str

    kwargs = {
        "position": tuple(yaml_dict["position"]),
        "spectrum": spectrum,
        "brightness": brightness,
    }
    if "params" in yaml_dict:
        kwargs["params"] = yaml_dict["params"]

    cls_map = {"Star": Star, "Sersic": Sersic}
    cls = cls_map.get(cls_name)
    if cls is None:
        raise ValueError(f"Unsupported target class: {cls_name}")

    return cls(**kwargs)
